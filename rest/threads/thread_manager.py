"""
A thread manager.
It waits for threads to finish and joins them, so that they do not become zombies.
"""

import threading
import time

class ThreadManager(object):
	"""
	The thread manager handles threads.
	It periodically polls threads to kill them, rather than have them become zombies.

	:ivar _threads: The list of threads that are currently running.
	:vartype _threads: list
	"""

	def __init__(self, threads):
		"""
		Create a container for the threads.

		:param threads: A shared list of threads.
			Deployed threads are stored in this list, and the manager routinely checks their status.
		:type threads: list
		"""

		self._threads = threads

	def run(self):
		"""
		Periodically check whether any thread has finished, or whether new ones should be created.
		"""

		try:
			while True:
				"""
				Poll the threads and check whether they have finished.
				"""
				i = 0
				while i < len(self._threads):
					thread = self._threads[i]
					if not thread.is_alive():
						thread.join()
						del self._threads[i]
					else:
						i += 1

				time.sleep(1)
		except KeyboardInterrupt:
			pass
