def components(card, n, fieldname):
    svalue = card.field(n)
    try:
        value = int(svalue)
    except:
        raise RuntimeError('%s (field #%s) on card must be an integer.\n'
                           'card=\n%s' % (fieldname, n) )

    svalue2 = str(value)
    svalue3 = ''.join(sorted(svalue2))
    for i,v in enumerate(svalue3):
        assert v not in svalue3[i+1:]
    return svalue3

def components_or_blank(card, n, fieldname, default=None):
    svalue = card.field(n)
    if svalue is None:
        return default
    elif isinstance(svalue, int):
        svalue = str(svalue)
    else:
        svalue = svalue.strip()

    if svalue:
        components(card, n, fieldname)
    else:
        return default

def blank(card, n, fieldname, default=None):
    svalue = card.field(n)
    if svalue is None:
        return default
    raise RuntimeError('%s = %s (field #%s) on card must be blank.' % (fieldname, svalue, n) )
    
def field(card, n, fieldname):
    return integer_double_string_or_blank(card, n, fieldname, default=None)

def integer_double_string_or_blank(card, n, fieldname, default=None):
    svalue = card.field(n)
    if svalue is None:
        return default
    elif isinstance(svalue, int) or isinstance(svalue, float):
        return svalue
    
    svalue = svalue.strip()
    if '.' in svalue:
        return double(card, field, n)
    elif svalue.isdigit():
        return int(svalue)
    elif len(svalue) == 0:
        return default
    else:
        return svalue

#def assert_int_bounded_range(card, n, fieldname, lower=None, upper=None):

def fields(f, card, fieldname, i, j=None):  ## TODO: improve fieldname
    fs = []
    if j is None:
        j = len(card)
    for ii in range(i,j):
        fs.append( f(card, ii, fieldname) )
    return fs

def fields_or_blank(f, card, fieldname, i, j=None, defaults=None):
    fs = []
    if j is None:
        j = len(card)
    
    assert j - i == len(defaults), 'j=%s i=%s j-i=%s len(defaults)=%s\ncard=%s' % (j,i,j-i, len(defaults), card)
    for ii, default in enumerate(defaults):
        fs.append( f(card, ii + i, fieldname + str(ii), default) )
    return fs

def integer(card, n, fieldname):
    try:
        svalue = card.field(n)
    except IndexError:
        raise RuntimeError('%s (field #%s) on card must be an integer.' % (fieldname, n) )

    try:
        return int(svalue)
    except:
        raise RuntimeError('%s = %s (field #%s) on card must be an integer.' % (fieldname, svalue, n) )

def integer_or_blank(card, n, fieldname, default=None):
    #try:
    svalue = card.field(n)
    #except IndexError:
    #    return default

    if isinstance(svalue, int):
        return svalue
    elif svalue is None:
        return default
    elif isinstance(svalue, str):
        try:
            return int(svalue)
        except:
            raise RuntimeError('%s = %s (field #%s) on card must be an integer.or blank.' % (fieldname, svalue, n) )
    return default
    
def double(card, n, fieldname):
    try:
        svalue = card.field(n)
    except IndexError:
        raise RuntimeError('%s (field #%s) on card must be an float.' % (fieldname, n) )
    if isinstance(svalue, float):
        return svalue

    #svalue = svalue.strip()
    try:  # 1.0, 1.0E+3, 1.0E-3
        value = float(svalue)
    except TypeError:
            raise RuntimeError('%s = %s (field #%s) on card must be an float.' % (fieldname, svalue, n) )
    except ValueError:
        try:
            svalue = svalue.upper()
            if 'D' in svalue:  # 1.0D+3, 1.0D-3
                svalue = svalue.replace('D','E')
                return float(svalue)

            # 1.0+3, 1.0-3
            sign = ''
            if '+' in svalue[0] or '-' in svalue[0]:
                svalue = svalue[1:]
                sign = svalue[0]
            if '+' in svalue:
                svalue = sign + svalue.replace('+','E+')
            elif '-' in svalue:
                svalue = sign + svalue.replace('-','E-')

            value = float(svalue)
        except ValueError:
            raise RuntimeError('%s = %s (field #%s) on card must be an float.' % (fieldname, svalue, n) )
    return value

def double_or_blank(card, n, fieldname, default=None):
    #try:
    svalue = card.field(n)
    #except IndexError:
        #return default

    if isinstance(svalue, float):
        return svalue
    elif isinstance(svalue, str):
        try:
            return double(card, n, fieldname)
        except:
            raise RuntimeError('%s = %s (field #%s) on card must be an float or blank.' % (fieldname, svalue, n) )
    return default
    
def double_or_string(card, n, fieldname):
    #try:
    svalue = card.field(n)
    #except IndexError:
        #raise RuntimeError('%s (field #%s) on card must be an float or string (not blank).' % (fieldname, n) )
    if isinstance(svalue, float):
        return svalue
    elif svalue is None:
        raise RuntimeError('%s (field #%s) on card must be an float or string (not blank).' % (fieldname, n) )

    if '.' in svalue: # float
        try:
            return double(card, n, fieldname)
        except:
            raise RuntimeError('%s = %s (field #%s) on card must be an float or string (not blank).' % (fieldname, svalue, n) )
    else: # string
        return svalue.strip()
    raise RuntimeError('%s = %s (field #%s) on card must be an float or string (not blank).' % (fieldname, svalue, n) )
    
def double_string_or_blank(card, n, fieldname, default=None):
    #try:
    svalue = card.field(n)
    #except IndexError:
        #return default
    if isinstance(svalue, float):
        return svalue
    elif svalue is None:
        return default

    if '.' in svalue:
        try:
            return double(card, n, fieldname)
        except:
            raise RuntimeError('%s = %s (field #%s) on card must be an float, string or blank.' % (fieldname, svalue, n) )
    else:
        return svalue
    return default
    
def integer_or_double(card, n, fieldname):
    #try:
    svalue = card.field(n)
    #except IndexError:
        #raise RuntimeError('%s (field #%s) on card must be an integer or float.' % (fieldname, n) )
    if isinstance(svalue, int) or isinstance(svalue, float):
        return svalue
    elif svalue is None:
        raise RuntimeError('%s (field #%s) on card must be an integer or float (not None).' % (fieldname, n) )

    if '.' in svalue:  # float/exponent
        try:
            double(card, n, fieldname)
        except ValueError:
            raise RuntimeError('%s = %s (field #%s) on card must be a integer or a float.' % (fieldname, svalue, n) )
    else:  # int
        try:
            value = int(svalue)
        except:           
            raise RuntimeError('%s = %s (field #%s) on card must be an integer or a float.' % (fieldname, svalue, n) )
    return value

def integer_double_or_blank(card, n, fieldname, default=None):
    #try:
    svalue = card.field(n)
    #except IndexError:
    #    return default

    if isinstance(svalue, int) or isinstance(svalue, float):
        return svalue
    elif svalue is None:
        return default

    if svalue:  # integer/float
        try:
            return integer_or_double(card, n, fieldname)
        except:
            raise RuntimeError('%s = %s (field #%s) on card must be an integer, float, or blank.' % (fieldname, svalue, n) )
    return default
    
def integer_or_string(card, n, fieldname):
    #try:
    svalue = card.field(n)
    #except IndexError:
        #raise RuntimeError('%s (field #%s) on card must be an integer or string.' % (fieldname, n) )
    if isinstance(svalue, int):
        return svalue

    if svalue.isdigit():  # int
        try:
            value = int(svalue)
        except ValueError:            
            raise RuntimeError('%s = %s (field #%s) on card must be an integer or string.' % (fieldname, svalue, n) )
    else:  # string
        return svalue
    return value

def integer_string_or_blank(card, n, fieldname, default=None):
    #try:
    svalue = card.field(n)
    #except IndexError:
        #return default
    if isinstance(svalue, int):
        return svalue
    elif svalue is None:
        return default

    if svalue.strip():  # integer/string
        try:
            return integer_or_string(card, n, fieldname)
        except:
            raise RuntimeError('%s = %s (field #%s) on card must be an integer, string, or blank.' % (fieldname, svalue, n) )
    return default

def integer_double_or_string(card, n, fieldname):
    #try:
    svalue = card.field(n)
    #except IndexError:
        #raise RuntimeError('%s (field #%s) on card must be an integer, float, or string.' % (fieldname, n) )
    if isinstance(svalue, int) or isinstance(svalue, float):
        return svalue
    
    svalue = svalue.strip()
    if svalue:  # integer/float/string
        if '.' in svalue:  # float
            value = double(card, n, fieldname)
        elif svalue.isdigit():  # int
            try:
                value = int(svalue)
            except ValueError:
                raise RuntimeError('%s = %s (field #%s) on card must be an integer, float, or string (not blank).' % (fieldname, svalue, n) )
        else:
            value = svalue
        return value
    raise RuntimeError('%s = %s (field #%s) on card must be an integer, float, or string (not blank).' % (fieldname, svalue, n) )

def integer_double_string_or_blank(card, n, fieldname, default=None):
    #try:
    svalue = card.field(n)
    #except IndexError:
        #raise RuntimeError('%s (field #%s) on card must be an integer, float, string, or blank.' % (fieldname, n) )

    if isinstance(svalue, int):
        return svalue
    elif svalue is None:
        return default
    elif isinstance(svalue, float):
        return svalue

    svalue = svalue.strip()
    if svalue:  # integer/float/string
        if '.' in svalue:  # float
            value = double(card, n, fieldname)
        elif svalue.isdigit():  # int
            try:
                value = int(svalue)
            except ValueError:
                raise RuntimeError('%s = %s (field #%s) on card must be an integer, float, or string.' % (fieldname, svalue, n) )
        else:
            value = svalue
        return value
    return default

def string(card, n, fieldname):
    svalue = card.field(n)
    if isinstance(svalue, str) or isinstance(svalue, unicode):
        svalue = svalue.strip()
    else:
        raise RuntimeError('%s = %s (field #%s) on card must be an string (not blank).' % (fieldname, svalue, n) )
    
    if svalue.isdigit() or '.' in svalue:
        raise RuntimeError('%s = %s (field #%s) on card must be an string or blank.' % (fieldname, svalue, n) )

    if svalue:  # string
        return svalue
    raise RuntimeError('%s = %s (field #%s) on card must be an string (not blank).' % (fieldname, svalue, n) )

def string_or_blank(card, n, fieldname, default=None):
    svalue = card.field(n)
    if svalue is None:
        return default
    elif isinstance(svalue, str) or isinstance(svalue, unicode):
        svalue = svalue.strip()
    else:
        raise RuntimeError('%s = %s (field #%s) on card must be an string (not blank).' % (fieldname, svalue, n) )

    svalue = svalue.strip()
    if svalue.isdigit() or '.' in svalue:
        raise RuntimeError('%s = %s (field #%s) on card must be an string or blank.' % (fieldname, svalue, n) )
        
    if svalue:  # string
        return svalue
    return default

# int                    - done
# int/blank              - done
# int/float              - done
# int/float/blank        - done
# int/float/string       - done
# int/float/string/blank - done
# int/string             - done
# int/string/blank       - done

# float              - done
# float/blank        - done
# float/string       - done
# float/string/blank - done

# string       - done
# string/blank - done

