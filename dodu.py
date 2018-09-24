def a(x):
    blah_name = [ k for k,v in locals().items() if v is x][0]
    print (blah_name)

class cccde:
    pass

a(cccde())
