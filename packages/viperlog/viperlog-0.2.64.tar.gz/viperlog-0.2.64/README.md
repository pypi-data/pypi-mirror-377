# VIPERLOG

This library is build on top of the python logging, 
it's not meant to replace it but rather make it easier to configure
and work together with it.  

This means that you can still use the build-in python getLogger for logging and no code changes are required apart from configuring this library.

## Installation
Some of the processors like console and http have additional dependencies
and are optionally installed. 

    pip install viperlog[all] # everything
    pip install viperlog[core] # The minimal core module which allows logging to file
    pip install viperlog[console] # console module
    pip install viperlog[http] # http module
    pip install viperlog[console,http] # http+console modules




## Usage

Get an instance of the Viperlog singleton class
    
    # both viperlog.logger.getLogger and logging.getLogger work the same
    import logging
    from viperlog import Viperlog, setup_viperlog_handler
    from viperlog.processors.console import ConsoleProcessor
    from viperlog.processors import FileProcessor
    from viperlog.formatters import JsonObjectFormatter
    
    # get a logger (normally this is the root logger, but you can attach the handlers any logger)
    logger = logging.getLogger()
    # make sure this logger is to the minumum level you want to log for all handlers, if you miss log messages then this is probably the cause.
    # it is also the most efficient way to filter on level, so if you can then set the minimum level here instead of leaving it to the viperlog handler
    logger.setLevel(logging.DEBUG)
    
    # Note on loglevel filtering, the loglevel set to the python logger is first.  Then the min_level on the handler
    # after those have been processed a PackageFilter can be used to customize the loglevels for specific namespaces.
    # The PackageFilter is the most flexible

    handler = setup_viperlog_handler("core-handler", 
                      logger=logger,  # the logger to attach the handler to
                      #min_level=logging.DEBUG, 
                      flush_level=logging.ERROR, # always flush if a message with this level comes in
                      processors=[
                         ConsoleProcessor(
                            # optional logging template
                            template="${datetime} [${level|upper}] [${name}] ${message}"
                         ),
                         FileProcessor(file="/var/log/mylog.txt"),
                         FileProcessor(
                              file="/var/log/mylog.json",
                              formatter=JsonObjectFormatter(
                                 template="${datetime} [${level|upper}] [${name}] ${message}"
                              )
                         )
                      ], 
                      # optional filters
                      filters=[ 
                            # package filters allow you to set the minimum log level for a namespace
                            # this is useful if you want different log levels for different processors
                            PackageFilter({
                                "pika":logging.INFO,
                                "my.other.namespace":logging.DEBUG,
                                # use an empty string as key to set the default level
                                # this can be usefull if you want to have a higher default then for some of the other namespaces
                                "":logging.INFO
                        }) 
                      ]
    )
    
    # you can attach the handler to more loggers if you need to
    handler.attach_to(...)
    # or remove it from all loggers it is attached to
    handler.detach_all()
So what does the setup_handler do?
It attaches a handler to the specified logger to process the messages.
- min_level: The minimum log level needed for messages to be processed
- flush_level: Records are processed in batches, if a message with this level comes in the buffer is flushed immediately. (So setting it to DEBUG or NOTSET effectively disables the buffer, alternatively if supports_batching = False in the IProcessor then the records will also be processed immediately)
- filters: Optional filters (viperlog.filters.IFilter protocol) to accept/reject messages based on the configuration. The PackageFilter in the example allows you to configure minimum log levels for namespaces without modifying the underlying logger instances. This can be useful if you would want different loglevels for different processors.
- processors: These instances of viperlog.processors.IProcessor take the messages, format and transport them to somewhere. The ConsoleProcessor will output to the console, the FileProcessor to a file etc.  

Most of the processors will accept a viperlog.formatters.IFormatter or a template string that will be used to format the log message 


You can call the setup_handler multiple times with different settings. In the above example the Console & File processors are combined, 
but you could setup separate handlers for them with different settings.


