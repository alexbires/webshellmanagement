from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader('php','.'))

def getTemplateContents(name):
	template = env.get_template('candidate.template')
	cprint template.render()