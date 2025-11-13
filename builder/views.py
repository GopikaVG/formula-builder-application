from django.shortcuts import render
from.models import variable,formula
# Create your views here.


def variablelist(request):
    datavar=variable.objects.all()
    

    return render(request,'variables.html',{'variables':datavar})

def formaddnewvariable(request):
    return render(request,'addnewvariable.html')

def addnewvariables(request):
    variabledata=variable()
    variabledata.name=(request.POST.get("name")).upper()
    variabledata.type=request.POST.get("type")
    value=request.POST.get("value")
    #need to ensure value is an number or another variable name
    if '.' in value:
        variabledata.value=float(value)
    elif value.isnumeric():
        variabledata.value=int(value)
    elif variable.objects.filter(name=value.upper()).exists():
        variabledata.value=value.upper()
    else:   
        return render(request,'addnewvariable.html',{'error':"Value must be a number or an existing variable name",'variable':variabledata})
   
    if (variable.objects.filter(name=variabledata.name)).exists():
        return render(request,'addnewvariable.html',{'error':"Variable with this name already exists.Does not allow duplicate values",'name':request.POST.get("name"), 'type':request.POST.get("type"), 'value':request.POST.get("value")})
    else:
        variabledata.save()
        data=variable.objects.all()
        return render(request,'variables.html',{'variables':data})

    
def variableedit(request):
    id=request.GET.get("id")
    variabledata=variable.objects.get(id=id)
    return render(request,'variableedit.html',{'variable':variabledata})

def variableupdate(request):
    id=request.POST.get("id")
    variabledata=variable.objects.get(id=id)
    variabledata.name=(request.POST.get("name")).upper()
    variabledata.type=request.POST.get("type")
    value=request.POST.get("value")
    # need to ensure it will be a number should accept both integer and floating point
    if '.' in value:
        variabledata.value=float(value)
    elif value.isnumeric():
        variabledata.value=int(value)
    elif variable.objects.filter(name=value).exists():
        variabledata.value=value
    else:   
        return render(request,'variableedit.html',{'error':"Value must be a number or an existing variable name",'variable':variabledata})

    # if value.isnumeric():
    #     variabledata.value=float(value)
    # elif variable.objects.filter(name=value).exists():
    #     variabledata.value=value
    # else:
    #     return render(request,'variableedit.html',{'error':"Value must be a number or an existing variable name",'variable':variabledata})

    if (variable.objects.filter(name=variabledata.name).exclude(id=id)).exists():
        return render(request,'variableedit.html',{'error':"Variable with this name already exists.Does not allow duplicate values",'variable':variabledata})
    else:
        variabledata.save()
        data=variable.objects.all()
        return render(request,'variables.html',{'variables':data})

def variabledelete(request):
    id=request.GET.get("id")
    variabledata=variable.objects.get(id=id)
    variabledata.delete()
    data=variable.objects.all()
    return render(request,'variables.html',{'variables':data})

def formulalist(request):
    dataformula=formula.objects.all()
    return render(request,'formulas.html',{'formulas':dataformula})

def formaddnewformula(request):
    return render(request,'addnewformula.html')



def addnewformula(request):
    formuladata=formula()
    formuladata.name=request.POST.get("name").upper()
    formuladata.expression=request.POST.get("expression").upper()
    expnames=formuladata.expression.replace('+', ' ')\
                                .replace('-', ' ')\
                                .replace('*', ' ')\
                                .replace('/', ' ')\
                                .replace('(', ' ')\
                                 .replace(')', ' ')\
                                .split()
    expnames=list(expnames)
    clean_names = []
    for name in expnames:
        #  Ignore placeholders like {{#NUM_OF_DAYS}}
        if name.startswith("{{#") and name.endswith("}}"):
            continue
        if name: 
            if not name.isdigit(): 
                clean_names.append(name)
    if clean_names and not variable.objects.filter(name__in=clean_names).exists():
        return render(request, 'addnewformula.html', {
            'error': "Expression contains undefined variables. Add them to the variables first.",
            'name': request.POST.get("name"),
            'expression': request.POST.get("expression")
        })
    else:
        formuladata.save()
        data = formula.objects.all()
        return render(request, 'formulas.html', {'formulas': data})
    
def formuladelete(request):
    id=request.GET.get("id")
    formuladata=formula.objects.get(id=id)
    formuladata.delete()
    data=formula.objects.all()
    return render(request,'formulas.html',{'formulas':data})

def evaluateformula(request):
    id = request.GET.get("id") or request.POST.get("id")
    formuladata = formula.objects.get(id=id)
    expression = formuladata.expression

    #  Detect contextual variables
    contextual_vars = []
    parts = expression.split("{{#")
    for p in parts[1:]:
        name = p.split("}}")[0]
        contextual_vars.append(name)
        expression = expression.replace(f"{{{{#{name}}}}}", name)  # replace placeholder with variable name

    # Extract normal variable names from expression
    var_names = expression.replace('+', ' ')\
                          .replace('-', ' ')\
                          .replace('*', ' ')\
                          .replace('/', ' ')\
                          .replace('(', ' ')\
                          .replace(')', ' ')\
                          .split()
    var_names = list(set(var_names + contextual_vars))  # remove duplicates
    variablesdata1 = variable.objects.filter(name__in=var_names)

    #  Identify which contextual variables are not in DB
    custom_vars = []
    for name in contextual_vars:
        if not variablesdata1.filter(name=name).exists():
            # create a dummy object for template rendering
            class DummyVar:
                def __init__(self, name, value=''):
                    self.name = name
                    self.value = value
            custom_vars.append(DummyVar(name))

    # Combine DB variables and dynamic variables from DB formulas
    formulanames = formula.objects.filter(name__in=var_names)
    variablesdata = list(variablesdata1)
    if formulanames.exists():
        subformula_names = []
        for f in formulanames:
            subexpr = f.expression
            subparts = subexpr.split("{{#")
            for p in subparts[1:]:
                subname = p.split("}}")[0]
                print( "SUBNAME:", subname)
                subformula_names.append(subname)
                subexpr = subexpr.replace(f"{{{{#{subname}}}}}", subname)
            # extract variables from subformula
            parts = subexpr.replace('+',' ').replace('-',' ').replace('*',' ').replace('/',' ').split()
            for p in parts:
                if p and p not in subformula_names:
                    subformula_names.append(p)
        baseconstants = variable.objects.filter(name__in=subformula_names)
        dynamic_vars = variablesdata1.filter(type='DYNAMIC')
        variablesdata = list(baseconstants) + list(dynamic_vars)

    return render(request, 'evaluateformula.html', {
        'formula': formuladata,
        'variables': variablesdata,
        'custom_vars': custom_vars,
      
        'show_inputs': True
    })


    
def evaluate(request):
    id = request.POST.get("id")
    # want to read values from input fields of each variables required for the expression and evaluate accoringly

    formuladata = formula.objects.get(id=id)
    expression = formuladata.expression
   

    # Extract variable names safely
    var_names = expression.replace('+', ' ').replace('-', ' ').replace('*', ' ').replace('/', ' ').split()
    var_names = list(set(var_names))  # Remove duplicates


    # Get variables and formula names present in the expression
    variablesdata = variable.objects.filter(name__in=var_names)
    formulanames = formula.objects.filter(name__in=var_names)


    # Create a dictionary for variables and their values which contain db values
    variables = {v.name: v.value for v in variablesdata}

    # get user input values for each field present and update variables dictionary
    for v in variablesdata:
        input_value = request.POST.get(f"var_{v.name}")
        print("INPUT VALUE:", input_value)
        if input_value is not None:
            # Convert to appropriate type
            if '.' in input_value:
                variables[v.name] = float(input_value)
            elif input_value.isnumeric():
                variables[v.name] = int(input_value)
            else:
                variables[v.name] = input_value  # keep as string if not a number
    


    # Evaluate formulas that appear as variables in the expression first
    for f in formulanames:
        # Recursively evaluate the formula's expression
        f_value = evaluatesub(f.expression)
        variables[f.name] = f_value


    # Replace variable/formula names with their values in the expression
    for name, val in variables.items():
        expression = expression.replace(name, str(val))



    # Safely evaluate the final expression
    try:
        result = eval(expression, {"__builtins__": None}, {})
    except Exception as e:
        result = f"Error evaluating expression: {str(e)}"
    # Prepare nested formula values for display
    vardisplay = []
    for v in variablesdata:
        v.displayvalue=variables.get(v.name, v.value)
        vardisplay.append(v)
    for f in formulanames:
        f.displayvalue=variables.get(f.name, '')
        vardisplay.append(f)
    #to avoid repetion of dynamicvariables in display
    vardisplay = list({v.name: v for v in vardisplay}.values())


    return render(request,'evaluateformula1.html',{'formula':formuladata,'variables':vardisplay,'result':result})

def evaluatesub(expression):
    # Helper recursive function to evaluate expression with nested formulas if needed
    var_names = expression.replace('+', ' ').replace('-', ' ').replace('*', ' ').replace('/', ' ').split()
    var_names = list(set(var_names))

    variablesdata = variable.objects.filter(name__in=var_names)
    formulanames = formula.objects.filter(name__in=var_names)

    variables = {v.name: v.value for v in variablesdata}

    for f in formulanames:
        f_value = evaluatesub(f.expression)
        variables[f.name] = f_value

    for name, val in variables.items():
        expression = expression.replace(name, str(val))

    
    return eval(expression, {"__builtins__": None}, {})
