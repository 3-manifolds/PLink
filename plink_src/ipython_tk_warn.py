def warn_if_necessary(tk_window, window_name):
    """
    When running within IPython, this function checks to see if a Tk event
    loop exists and, if not, tells the user how to start one.
    """
    try:
        import IPython, threading, time
        ip = IPython.get_ipython()

        tk_window._have_tk = False

        def set_flag():
            tk_window._have_tk = True
        
        def ipython_tk_check():
            message = ('Your new ' + window_name +
                       ' window needs an event loop to become visible and active.\n' + 
                       'Type "%gui tk" below (without the quotes) to start one.\n')
            if IPython.version_info < (6,):
                message = '\n' + message[:-1]
            time.sleep(1)
            if not tk_window._have_tk:
                print("\x1b[31m%s\x1b[0m"%message)

        # Tk will set the flag if it is has an event loop.
        tk_window.after(100, set_flag)
        # This thread will notice if the flag did not get set.
        threading.Thread(target=ipython_tk_check).start()
        
    except ImportError:
        pass
