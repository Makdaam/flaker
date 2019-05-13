from flaker import flaker

@flaker.route('/')
@flaker.route('/index')
def index():
    return "Flaker works 2"
