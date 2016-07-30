import argparse
import mmap
import os
import re
import subprocess

try:
	from termcolor import colored
except ImportError:
	def colored(text, color=None, on_color=None, attrs=None):
		return text


def config():
	parser = argparse.ArgumentParser(description='Find regex in files.')
	parser.add_argument('regex', help='Regular expression to be found in the files.')
	return parser.parse_args()


def files_find(path):
	return subprocess.check_output(['find', path, '-type', 'f']).decode().split('\n')[:-1]


def files_walk(path):
	for file_path, __, file_names in os.walk(path.rstrip('/')):
		for file_name in file_names:
			yield os.sep.join([file_path, file_name])


def files(path):
	for file_name in files_walk(path):
		if file_name.startswith('./.git'):
			continue
		if 0 == os.stat(file_name).st_size:
			continue
		yield file_name


def find_in_file(file_name, needle):
	with open(file_name, 'r') as file_handle:
		with mmap.mmap(file_handle.fileno(), 0, prot=mmap.PROT_READ) as file_mmap:
			start, lineno = 0, 1
			for match in re.finditer(needle, file_mmap):
				while start < match.start():
					position = file_mmap.find(b'\n', start, match.start())
					if -1 == position:
						break
					lineno += 1
					start = position + 1
				file_mmap.seek(start)
				lines = []
				for __ in match.group(0).decode().split('\n'):
					lines.append((lineno, file_mmap.readline().decode()[:-1]))
					lineno += 1
				yield lines
				lineno -= 1
				start = match.end()


def main(needle):
	with subprocess.Popen(['less', '--no-init', '--quit-if-one-screen'], stdin=subprocess.PIPE) as pager:

		def echo(message=''):
			pager.stdin.write((str(message) + '\n').encode())
			pager.stdin.flush()

		for file_name in files('./'):
			first_result = True
			for result in find_in_file(file_name, needle):
				if first_result:
					echo(colored(file_name, 'red', attrs=['bold']))
					first_result = False
				for line_number, line in result:
					echo(colored(str(line_number) + ':', 'green') + line)
				echo()


if '__main__' == __name__:
	config = config()
	main(re.compile(config.regex.encode(), re.MULTILINE))
