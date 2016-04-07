import sys
import os
import json
import shutil as sh

def get_parm(parmkey,record):
  """ Helper function for reset_naming().
  Gets parameter from record.json dictionary."""
  parm = ""
  if parmkey in record['qmc']['dmc'].keys():
    parm = record['qmc']['dmc'][parmkey]
  else:
    sys.exit("Don't know how to handle this key: %s ."%parmkey)
  if type(parm) == list:
    if len(parm)>1:
      print("Error: you used multiple %s,"%parmkey,)
      print("and I don't know how to seperate which is which.")
      sys.exit()
    parm = parm[0]
  return parm

def find_only_int(strlist):
  """ Helper: finds int in list of strings, error if there not exactly one. """
  res = -10000000
  found_already = False
  for item in strlist:
    try:
      res = int(item)
      if found_already:
        print("Two ints in list. Unambiguous result.")
        print(strlist)
        raise AssertionError
      else:
        found_already = True
    except ValueError:
      pass
  if res == -10000000:
    print("Found no ints in this list.")
    print(strlist)
    raise AssertionError
  return res

# Copied from runqwalk.py.
def gen_basename(k,t,loc,jast,opt):
  return "qw_%i_%s_%g_%s_%s"%(k,jast,t,opt,loc)
def gen_optbase(k,jast):
  return "qw_%i.%s"%(k,jast)

def reset_naming(ag_dir):
  """
  Reset naming of autogen files to be consistent with existing record.json and
  whatever naming scheme is hard coded in here.
  """
  # Read in and extract data from record.json.
  record = json.load(open("/".join((ag_dir,"record.json"))))

  dat = {}
  for parmkey in ['timestep','optimizer','jastrow','localization']:
    dat[parmkey] = get_parm(parmkey,record)


  # Move all files that require new names to be consistent with new scheme.
  flist = os.listdir(ag_dir)
  flist = [f for f in flist if "stdout" not in f]
  dmclist   = [f for f in flist if ".dmc" in f]
  enoptlist = [f for f in flist if ("enopt" in f) and ("qw" in f)]
  optlist   = [f for f in flist if ("opt" in f) and ("qw" in f) and (f not in enoptlist)]
  print(optlist)
  dmcbase   = [f[:f.find(".dmc")]   for f in dmclist]
  enoptbase = [f[:f.find(".enopt")] for f in enoptlist]
  optbase   = [f[:f.find(".opt")]   for f in optlist]
  for didx, dmcfn in enumerate(dmclist):
    print("Old: %s"%dmcfn)
    kpt = find_only_int(dmcbase[didx].split('_'))
    newfn = dmcfn.replace(dmcbase[didx],
      gen_basename(
        kpt, 
        float(dat['timestep']),
        dat['localization'],
        dat['jastrow'],
        dat['optimizer']
      ))
    print("New: %s"%newfn)
    sh.move('/'.join((ag_dir,dmcfn)),'/'.join((ag_dir,newfn)))

  for oidx, optfn in enumerate(optlist):
    print("Old: %s"%optfn)
    if "_0" not in optfn: 
      print("I'm only set to deal with gamma-point optimziations!")
      raise AssertionError
    newfn = optfn.replace(optbase[oidx], gen_optbase(0,dat['jastrow']))
    print("New: %s"%newfn)
    sh.move('/'.join((ag_dir,optfn)),'/'.join((ag_dir,newfn)))

  for oidx, enoptfn in enumerate(enoptlist):
    print("Old: %s"%enoptfn)
    if "_0" not in enoptfn: 
      print("I'm only set to deal with gamma-point optimziations!")
      raise AssertionError
    newfn = enoptfn.replace(enoptbase[oidx], gen_optbase(0,dat['jastrow']))
    print("New: %s"%newfn)
    sh.move('/'.join((ag_dir,enoptfn)),'/'.join((ag_dir,newfn)))

  print("Finished renaming successfully.")

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("Usage: python reset_naming.py <list of dirs>")
  for ag_dir in sys.argv[1:]:
    reset_naming(ag_dir)
