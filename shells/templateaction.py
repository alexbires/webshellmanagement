from jinja2 import Environment, PackageLoader


env = Environment(loader=PackageLoader('php','.'))
template = env.get_template('candidate.template')
print template.render()