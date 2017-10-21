def getBuildAndRevision(e):
   "Gets the environment name, then decides and returns build and revision names"
   buildRev = []
   if e == "Test":
    buildRev = ["test","test"]
   elif e == "Dev":
    buildRev = ["development","develop"]
   elif e == "Uat":
    buildRev = ["uat","uat"]
   elif e == "Prod":
    buildRev = ["production","prod"]
   return buildRev