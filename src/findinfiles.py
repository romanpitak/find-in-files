import mmap
import re
import subprocess
import sys

try:
	from termcolor import colored
except ImportError:
	def colored(text, color=None, on_color=None, attrs=None):
		return text


def files(path):
	for file_name in subprocess.check_output(['find', path, '-type', 'f']).decode().split('\n')[:-1]:
		if file_name.startswith('./.git'):
			continue
		yield file_name


def find_in_file(file_name, needle):
	with open(file_name, 'r') as file_handle:
		file_mmap = mmap.mmap(file_handle.fileno(), 0, prot=mmap.PROT_READ)
		results = [x for x in re.finditer(needle, file_mmap)]
		if results:
			start, lineno = 0, 1
			for match in results:
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
	main(re.compile(sys.argv[1].encode(), re.MULTILINE))
