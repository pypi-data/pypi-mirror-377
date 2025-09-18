================
Source Factories
================

Source factories are used to simplify the creation of sources for certain
standard cases.

Sources split up the process of providing input fields with choices for users
into several components: a context binder, a source class, a terms class, and a
term class.

This is the correct abstraction and will fit many complex cases very well. To
reduce the amount of work to do for some standard cases, the source factories
allow users to define only the business relevant code for getting a list of
values, getting a token and a title to display.
