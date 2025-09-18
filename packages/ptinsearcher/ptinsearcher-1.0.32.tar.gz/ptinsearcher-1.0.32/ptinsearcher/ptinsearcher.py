#!/usr/bin/python3
"""
Copyright (c) 2025 Penterep Security s.r.o.

ptinsearcher - Web / File information extractor

ptinsearcher is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ptinsearcher is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ptinsearcher. If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import os
import re
import sys; sys.path.append(__file__.rsplit("/", 1)[0])
import urllib
import requests
from concurrent.futures import ThreadPoolExecutor
import threading

from ptlibs import ptmisclib, ptjsonlib, ptprinthelper
from modules import _website_scraper, _files_scraper, metadata, results

from modules._website_scraper import WebsiteScraper
from modules._files_scraper import FileScraper
from modules.results.results import print_result

from modules.cli.extract_flags import parse_extract_flags
from modules.cli.args_validator import validate_args

from _version import __version__

class PtInsearcher:
    def __init__(self, args):
        self.ptjsonlib                = ptjsonlib.PtJsonLib()
        self.url_list                 = self._get_url_list(args)
        self.args                     = args
        self.things_to_extract: dict  = args.extract
        self.use_json                 = args.json
        self.group_parameters         = args.group_parameters
        self.without_parameters       = args.without_parameters

        self.file_handler             = open(args.output, "w") if args.output and not args.output_parts else None
        self.lock                     = threading.Lock()

    def run(self, args: argparse.Namespace):
        if len(self.url_list) == 1:
            self.args.threads = 1

        # Paralell processing of targets
        result_list: list = [result for result in self.process_targets(targets=self.url_list)]

        # Print results if grouping is enabled or multiple results with grouping_complete - for summary
        if (args.grouping) or (len(result_list) > 1 and args.grouping_complete):
            print_result(result_list, args)

        self.ptjsonlib.set_status("finished")
        ptprinthelper.ptprint(self.ptjsonlib.get_result_json(), "", self.use_json)

    def process_targets(self, targets: list[str]):
        """
        Processes multiple targets concurrently using ThreadPoolExecutor.

        Parameters:
            targets (list[str]): A list of URLs or file paths to process.

        Returns:
            list: A list of results from processing each target.
        """
        results = []

        with ThreadPoolExecutor(max_workers=self.args.threads) as executor:
            future_to_target = {executor.submit(self.process_target, target): target for target in targets}
            for future in future_to_target:
                try:
                    result = future.result()
                    if result:
                        with self.lock:
                            results.append(result)
                            if not self.args.grouping: # if not -g
                                print_result([result], self.args) # Print output continuously
                except Exception as e:
                    ptprinthelper.ptprint(f"Error processing {future_to_target[future]}: {e}", "ERROR")
        return results

    def process_target(self, target: str):
        """
        Processes the given target, identifying it as either a URL or a file path.

        This method checks if the `target` is a valid URL or an existing file.
        It then processes the target appropriately:
        - For URLs: Scrapes the website using `self.website_scraper`.
        - For files: Processes the file using `scrape_files.FileScraper`.

        Parameters:
            target (str): The source to be processed, which can be a URL or a local file path.

        Returns:
            Any: The result of scraping or file processing.

        Raises:
            ValueError: If the target does not represent a valid URL or file and error handling is triggered.
        """
        if self._target_is_url(target):
            scrape_result = WebsiteScraper(args=self.args, things_to_extract=self.things_to_extract, url_list_len=len(self.url_list), ptjsonlib=self.ptjsonlib, lock=self.lock).scrape_url(url=target)
            return scrape_result

        elif self._target_is_file(target):
            scrape_result = FileScraper(args=self.args, things_to_extract=self.things_to_extract, ptjsonlib=self.ptjsonlib, lock=self.lock).process_file(path_to_local_file=os.path.abspath(target), args=self.args, ptjsonlib=self.ptjsonlib)
            return scrape_result

        else:
            error_message = f"{target} is neither an existing file nor a valid URL."
            if len(self.url_list) > 1:
                ptprinthelper.ptprint(error_message, "ERROR")
                return
            self.ptjsonlib.end_error(error_message, self.use_json)

    def _target_is_file(self, source: str) -> bool:
        """Check whether the provided source is an existing file"""
        return os.path.isfile(source)

    def _target_is_url(self, source: str) -> bool:
        """Check whether the provided source is a valid URL"""
        regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?' # optional ports
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return regex.match(source)

    def _get_url_list(self, args) -> list:
        """Generates a list of URLs based on the provided arguments."""
        if args.url:
            return args.url
        elif args.file:
            try:
                url_list = self._read_file(args.file, args.domain)
                if args.extension_yes:
                   url_list = list(dict.fromkeys([url for url in url_list if url.endswith(tuple(args.extension_yes))]))
                if args.extension_no:
                    url_list = list(dict.fromkeys([url for url in url_list if not url.endswith(tuple(args.extension_no))]))
                return list(dict.fromkeys(url_list))
            except Exception as e:
                self.ptjsonlib.end_error("Error reading from provided file.", args.json)

    def _read_file(self, filepath, domain) -> list:
        domain = self._normalize_domain(domain) if domain else None
        target_list = []
        try:
            with open(filepath, "r") as f:
                for line in f:
                    line = line.strip("\n")
                    if domain:
                        path = urllib.parse.urlparse(line).path
                        while path.startswith("/"): path = path[1:]
                        while path.endswith("/"): path = path[:-1]
                        if not path: continue
                        target_list.append(domain + path)
                    else:
                        if re.match(r'https?://', line):
                            while line.endswith("/"): line = line[:-1]
                            target_list.append(line)
            return target_list
        except FileNotFoundError:
            self.ptjsonlib.end_error(f"File not found {os.path.join(os.getcwd(), self.args.file)}", self.use_json)

    def _normalize_domain(self, domain: str) -> str:
        """Adjusts provided <domain>"""
        o = urllib.parse.urlparse(domain)
        if not re.match("http[s]?$", o.scheme):
            self.ptjsonlib.end_error(f"Missing or invalid scheme, supported schemes are: [HTTP, HTTPS]", self.use_json)
        return domain + "/" if not o.path.endswith("/") else domain


def get_help():
    return [
        {"description": ["Source information extractor"]},
        {"usage": ["ptinsearcher <options>"]},
        {"usage_example": [
            "ptinsearcher -u https://www.example.com/",
            "ptinsearcher -u https://www.example.com/ --extract E        # Extract emails",
            "ptinsearcher -u https://www.example.com/ --extract UQX      # Extract internal URLs, internal URLs w/ parameters, external URLs",
            "ptinsearcher -f url_list.txt --grouping                     ",
            "ptinsearcher -f url_list.txt --grouping-complete            ",
            "ptinsearcher -f url_list.txt",
            "ptinsearcher -u image.jpg -e M",
            "ptinsearcher -u images/*.jpg -e M",
        ]},
        {"options": [
            ["-u",  "--url",                    "<url>",            "Test URL or File"],
            ["-f",  "--file",                   "<file>",           "Load list of URLs from file"],
            ["-d",  "--domain",                 "<domain>",         "Domain - merge domain with filepath. Use when wordlist contains filepaths (e.g. /index.php)"],
            ["-e",  "--extract",                "<extract>",        "Specify data to extract:"],
            ["",    "",                         "   A",             "  All (extracts everything - default option)"],
            ["",    "",                         "   E",             "  Emails"],
            ["",    "",                         "   S",             "  Subdomains"],
            ["",    "",                         "   C",             "  Comments"],
            ["",    "",                         "   F",             "  Forms"],
            ["",    "",                         "   I",             "  IP addresses"],
            ["",    "",                         "   P",             "  Phone numbers"],
            ["",    "",                         "   U",             "  Internal urls"],
            ["",    "",                         "   Q",             "  Internal urls with parameters"],
            ["",    "",                         "   X",             "  External urls"],
            ["",    "",                         "   N",             "  Insecure urls"],
            ["",    "",                         "   M",             "  Metadata"],
            ["",    "",                         "   K",             "  Google Keys"],
            ["",    "",                         "",                 ""],
            ["-s",  "--search",                 "<re>",             "Search for provided regex."],
            ["-ey", "--extension-yes",          "<extensions>",     "Process only URLs from <list> that end with <extension-yes>"],
            ["-en", "--extension-no",           "<extensions>",     "Process only URLs from <list> that do not end with <extension-no>"],
            ["-g",  "--grouping",               "",                 "Group findings from multiple sources into one table"],
            ["-gc", "--grouping-complete",      "",                 "Group and merge findings from multiple sources into one result"],
            ["-gp", "--group-parameters",       "",                 "Group URL parameters"],
            ["-wp", "--without-parameters",     "",                 "Without URL parameters"],
            ["-op", "--output-parts",           "",                 "Save each extract-type to separate file"],
            ["-o",  "--output",                 "<output>",         "Save output to file"],
            ["-vv",  "--very-verbose",          "",                 "Enable very verbose output"],

            ["-p",  "--proxy",                  "<proxy>",          "Set proxy (e.g. http://127.0.0.1:8080)"],
            ["-T",  "--timeout",                "<timeout>",        "Set timeout"],
            ["-c",  "--cookie",                 "<cookie=value>",   "Set cookie"],
            ["-a",  "--user-agent",             "<user-agent>",     "Set User-Agent"],
            ["-t",  "--threads",                "<threads>",        "Set Threads"],
            ["-H",  "--headers",                "<header:value>",   "Set custom header(s)"],
            ["-r",  "--redirects",              "",                 "Follow redirects (default False)"],
            ["-C",  "--cache",                  "",                 "Cache requests (load from tmp in future)"],
            ["-v",  "--version",                "",                 "Show script version and exit"],
            ["-h",  "--help",                   "",                 "Show this help message and exit"],
            ["-j",  "--json",                   "",                 "Output in JSON format"],
        ]
        }]


def parse_args():
    parser = argparse.ArgumentParser(add_help=False, usage=f"{SCRIPTNAME} <options>")
    parser.add_argument("-u",  "--url",                type=str, nargs="+")
    parser.add_argument("-f",  "--file",               type=str)
    parser.add_argument("-d",  "--domain",             type=str)
    parser.add_argument("-e",  "--extract",            type=str, default="A")
    parser.add_argument("-ey", "--extension-yes",      type=str, nargs="+")
    parser.add_argument("-en", "--extension-no",       type=str, nargs="+")
    parser.add_argument("-pd", "--post-data",          type=str)
    parser.add_argument("-o",  "--output",             type=str)
    parser.add_argument("-s",  "--search",             type=str)
    parser.add_argument("-p",  "--proxy",              type=str)
    parser.add_argument("-T",  "--timeout",            type=int)
    parser.add_argument("-t",  "--threads",            type=int, default=5)
    parser.add_argument("-c",  "--cookie",             type=str, nargs="+")
    parser.add_argument("-a",  "--user-agent",         type=str, default="Penterep Tools")
    parser.add_argument("-H",  "--headers",            type=ptmisclib.pairs, nargs="+")

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("-g",  "--grouping",           action="store_true")
    group.add_argument("-gc", "--grouping-complete",  action="store_true")

    parser.add_argument("-r",  "--redirects",          action="store_true")
    parser.add_argument("-op", "--output-parts",       action="store_true")
    parser.add_argument("-gp", "--group-parameters",   action="store_true")
    parser.add_argument("-wp", "--without-parameters", action="store_true")
    parser.add_argument("-vv",  "--very-verbose",          action="store_true")

    parser.add_argument("-C",  "--cache-requests",     action="store_true")
    parser.add_argument("-j",  "--json",               action="store_true")
    parser.add_argument("-v",  "--version",            action="version", version=f"%(prog)s {__version__}", help="show version")

    parser.add_argument("--socket-address",          type=str, default=None)
    parser.add_argument("--socket-port",             type=str, default=None)
    parser.add_argument("--process-ident",           type=str, default=None)


    if len(sys.argv) == 1 or "-h" in sys.argv or "--help" in sys.argv:
        ptprinthelper.help_print(get_help(), SCRIPTNAME, __version__)
        sys.exit(0)

    args = parser.parse_args()
    _ptjsonlib = ptjsonlib.PtJsonLib()

    args.extract: dict = parse_extract_flags(
        args=args,
        extract_str=args.extract,
        on_error=lambda msg: _ptjsonlib.end_error(msg, args.json)
        )

    ptprinthelper.print_banner(SCRIPTNAME, __version__, args.json, space=0)
    return args


def main():
    global SCRIPTNAME
    SCRIPTNAME = "ptinsearcher"
    requests.packages.urllib3.disable_warnings()
    args = parse_args()
    script = PtInsearcher(args)
    script.run(args)


if __name__ == "__main__":
    main()
