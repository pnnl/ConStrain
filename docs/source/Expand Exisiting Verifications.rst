Expand Exisiting Verifications
===============================

.. role:: python(code)
   :language: python

1. A new verification logic file should be added to the `contrain/library` folder which already includes several verification logic
  - At a minimum (for rule-based verification) the logic should be wrapped into a :python:`verify()` function as shown below where :python:`df` is a :python:`pandas.DataFrame` that contains the data needed for the verification
  - For more complicated verifications (e.g., procedure-based) the functions in the :meth:`checklib.CheckLibBase` class can be overloaded

.. sourcecode:: python

    from constrain.checklib import RuleCheckBase


    class NewVerificationLogicClassName(RuleCheckBase):
        points = ["point_1", "point_2"]

        def verify(self):
            self.result = (self.df["point_1"] > self.df["point_2"])
    
2. The new verification class name should be added to the list of class already listed in the `__init__.py` file located in that same directory
3. A library file that includes all the information needed by the verification logic should be created or appended if it already exists
