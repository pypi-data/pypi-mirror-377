from flask import Flask
from sdtp import sdtp_server_blueprint
from server_test_tables import test_tables
app = Flask(__name__)
app.register_blueprint(sdtp_server_blueprint)


if __name__ == '__main__':
  sdtp_server_blueprint.init_logging(__name__)
  for table_spec in test_tables:
    sdtp_server_blueprint.table_server.add_sdtp_table(table_spec)
  app.run(debug=True, port=5000)