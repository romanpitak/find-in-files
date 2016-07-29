import mmap
import re
import subprocess
import sys

try:
	from termcolor import colored
except ImportError:
	def colored(text, color=None, on_color=None, attrs=None):
		return text

rrr = re.compile(sys.argv[1].encode(), re.MULTILINE)

with subprocess.Popen(['less', '--no-init', '--quit-if-one-screen'], stdin=subprocess.PIPE) as pager:

	def echo(message=''):
		pager.stdin.write((str(message) + '\n').encode())

	for file_name in subprocess.check_output(['find', './', '-type', 'f']).decode().split('\n')[:-1]:
		if file_name.startswith('./.git'):
			continue
		with open(file_name, 'r') as file_handle:
			data = mmap.mmap(file_handle.fileno(), 0, prot=mmap.PROT_READ)
			res = [x for x in re.finditer(rrr, data)]
			if res:
				echo(colored(file_name, 'red', attrs=['bold']))
				start, lineno = 0, 1
				for x in res:
					while start < x.start():
						position = data.find(b'\n', start, x.start())
						if -1 == position:
							break
						lineno += 1
						start = position + 1
					data.seek(start)
					for line in x.group(0).decode().split('\n'):
						echo(colored(str(lineno) + ':', 'green') + data.readline().decode()[:-1])
						lineno += 1
					lineno -= 1
					start = x.end()
					echo()
