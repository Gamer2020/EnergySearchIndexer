import yaml

# Read the configuration data from the file
with open('config.yml') as config_file:
    config_data = yaml.load(config_file, Loader=yaml.FullLoader)

# Access the value of the list in the configuration data

config_api_url: config_data['api_url']
config_api_version: config_data['api_version']
config_api_key: config_data['api_key']

config_youtube_channels = config_data['config']['youtube_channels']
