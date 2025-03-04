import json

def argsort_names(names):
	# augment with index
	inames = [(name,i) for i,name in enumerate(names)]
	def last_name_first(iname):
		names = iname[0].split()
		return (names[-1],)+tuple(names[:-1])
	# Do the actual sorting
	inames = sorted(inames, key=last_name_first)
	# Unpack indices
	return [i for name,i in inames]

def initials(name):
	return "".join([word[0] for word in name.replace("_"," ").split()])

def comma_and(words):
	if len(words) == 1: return words[0]
	else: return ", ".join(words[:-1]) + " and " + words[-1]

def format_author_tex(name, orcid):
	orcstr = "[%s]" % orcid if orcid else ""
	return "\\author%s{%s}" % (orcstr, name.replace("_"," ").replace(" ", "~"))

def format_affil_tex(affil):
	return "\\affiliation{%s}" % affil

def build_authaffil(db, auth_levels):
	authdb  = db["authors"]
	affildb = db["institutions"]
	lines = []
	for level, authids in enumerate(auth_levels):
		# Will sort each level alphabetically by last name
		names = [authdb[authid][0] for authid in authids]
		order = argsort_names(names)
		for ind in order:
			authinfo = authdb[authids[ind]]
			auth_tex = format_author_tex(name=authinfo[0], orcid=authinfo[1])
			affil_tex = [format_affil_tex(affildb[affil]) for affil in authinfo[2]]
			full_tex = auth_tex + " " + " ".join(affil_tex)
			lines.append(full_tex)
	return lines

def build_ackn(db, auth_levels):
	authdb  = db["authors"]
	ackndb  = db["acknowledgements"]
	# For each acknowledgement, find all authors who apply
	acknmap = {}
	acknpri = {}
	priority= 0
	for level, authids in enumerate(auth_levels):
		names = [authdb[authid][0] for authid in authids]
		order = argsort_names(names)
		for ind in order:
			authinfo = authdb[authids[ind]]
			for acknid in authinfo[3]:
				if acknid not in acknmap:
					acknmap[acknid] = []
					acknpri[acknid] = priority
				acknmap[acknid].append(authids[ind])
				priority += 1
	# Sort them by priority. This will place the main authors'
	# acknowledgements earlier. Not important, but we want some
	# predictable order.
	sorted_acknids = sorted(acknmap.keys(), key=lambda key: acknpri[key])
	# Ok, loop through each of the acknowlegements that were actually
	# acknowledged by anybody
	lines = []
	for i, acknid in enumerate(sorted_acknids):
		authids = acknmap[acknid]
		nauth   = len(authids)
		trail_s = ""    if nauth > 1 else "s"
		is_are  = "are" if nauth > 1 else "is"
		# Generate the format replacements
		formats = {}
		# First the author initials
		formats["author"] = comma_and([initials(authdb[authid][0]) for authid in authids])
		formats["ackn"]   = "acknowledge" + trail_s
		formats["thank"]  = "thank" + trail_s
		formats["is"]     = is_are
		line = ackndb[acknid].format(**formats) + "."
		lines.append(line)
	return lines

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("dbfile")
	parser.add_argument("authlist")
	args = parser.parse_args()
	with open(args.dbfile, "r") as dbfile:
		db = json.load(dbfile)
	auth_levels = []
	with open(args.authlist, "r") as aufile:
		for line in aufile:
			auth_levels.append([aid.strip() for aid in line.split(",")])
	authors = build_authaffil(db, auth_levels)
	print("\n".join(authors))
	print()
	ackns   = build_ackn     (db, auth_levels)
	print("\n".join(ackns))


