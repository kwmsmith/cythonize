----------------
Post-import Hook
----------------

from: http://blog.cdleary.com/2009/04/monstrous-polymorphism-and-a-python-post-import-hook-decorator/

There is no standard post-import hook (that I know of) in Python. PEP 369 looks
promising, but I couldn’t find any record of additional work being done on it.
The current import hooks, described in PEP 302, are all pre-import hooks. As
such, you have to decorate the __import__ builtin, wrapping the original with
your intended post-input functionality, like so::

 def import_decorator(old_import, post_processor):
     """
     :param old_import: The import function to decorate, most likely
         ``__builtin__.__import__``.
     :param post_processor: Function of the form
         `post_processor(module) -> module`.
     :return: A new import function, most likely to be assigned to
         ``__builtin__.__import__``.
     """
     assert all(callable(fun) for fun in (old_import, post_processor))
     def new_import(*args, **kwargs):
         module = old_import(*args, **kwargs)
         return post_processor(module)
     return new_import

After which we can replace the old __import__ with its decorated counterpart::

 __builtin__.__import__ = import_decorator(__builtin__.__import__,
     extend_monsters)
