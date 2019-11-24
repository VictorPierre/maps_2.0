import logging
import sys, getopt

##load the web app
from routes import app

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:],"d",["debbug"])
        opts = [opt[0] for opt in opts]
    except getopt.GetoptError as e:
        logging.error(e)
        sys.exit(2)

    if '-d' in opts or '--debbug' in opts:
        logging.basicConfig(level=logging.INFO)
        app.run(debug=True)
    else:
        logging.basicConfig(level=logging.WARNING)
        app.run(debug=False)