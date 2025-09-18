def add(a,b):
    """this is a basic add function"""
    return a+b

def sub(a,b):
    """this is a basic subtraction function"""
    return a-b

def mul(a,b):
    """this is a basic multiplication function function"""
    return a*b

def div(a,b):
    """this is a basic division function"""
    if b==0:
        raise ValueError("this is not possible please change val of b")
    return a/b

def pow(a,b):
    """this is going to return power of a function"""
    return a**b

## here our main moto is to create our own custom package and need to push to pypi so that whoever install ourpacakage can able to 
#access the methods in it
#for that first create a package with name ex"maycal"
#after that create a module i.e, file ex: calculator.py and add some of the whatever we want
# after doing this create __init__.py to initialize the module 
#Once after doing this we need to create setup file for to push it into pypi
#in setup.py file we have mentioned Readme file so that where we included python package install command
#Later we need to do the project setup 
#for to do a project setup we need to install couple of things in our local environment first
#after create the requirements.py file

#whenever we are trying to create our own packages inside our system python allows us to create a different kind of an
#environment for a individual project

#then inside that seperate environment whatever requirement that we have the respect to this particular project
#we can try to install only those requirements we dont have to install each and everything , only required things for this environment
