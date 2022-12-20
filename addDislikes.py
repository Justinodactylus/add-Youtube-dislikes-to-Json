import sys, os, getopt, json, requests, time

def parseArguments(argv):
    input_str = ''

    try:
        options, arguments = getopt.getopt(argv, "hi:",["--help","input-file="])
    except getopt.GetoptError:
        print("Usage: addDislikes.py -i <inputFile/directory>")
        sys.exit(2)
    for option, argument in options:
        if option in ("-h","--help"):
            print("Usage: addDislikes.py -i <inputFile/directory>")
            sys.exit()
        elif option in ("-i","--input-file"):
            input_str = argument
    
    #print("The input file is: '",input_str, "'")
    return input_str

def extractFiles(filename, fileExtension):
    filename = os.path.abspath(filename)
    filenames = []

    if os.path.isfile(filename):
        filenames.append(filename)
    elif os.path.isdir(filename):
        for root, directory, files in os.walk(filename):
            for file in files:
                if file.endswith(fileExtension):
                    filenames.append(os.path.join(root, file))
    else:
        print("No valid file or directory is given, please try again with a valid file or directory")
        sys.exit(2)
    return filenames

def apiGETRequest(url, parameters):
    # does a request with the following url: url + '?' + firstArgumentName + '=' + firstArgumentValue +
    # '&' + secondArgumentName + ';=' + secondArgumentValue. F.e. 'https://api.open-notify.org/this-api-doesnt-exist?lat=34.3&lon;=-74'
    response = requests.get(url, params=parameters)
    if response.status_code == 200:
        #print(response.json())
        return response.json()
    elif response.status_code == 429: # too many requests
        seconds = 10
        print("Rate limited, waiting", seconds, "seconds...")
        time.sleep(seconds)
        return apiGETRequest(url, parameters)
    else:
        print("Request was not successful. Throwed a status code '", response.status_code, "'")

def appendDataToJson(file_dict, insert_pos_key, data):
    # append data to existing json 
    try:
        res = dict()
        for key, value in file_dict.items():
            res[key] = value

            # modify after adding parameter key
            if key == insert_pos_key:
                # insert all key value pairs of 'data'
                for k, v in data.items():
                    res[k] = v
        return res
    except KeyError:
        print("No parameter '", insert_pos_key, "'in dictionary found")

def getVideoIDfromJson(file_dict, parameter):
    # load existing data
    try:
        #print("parameters value: ", file_dict[parameter])
        return file_dict[parameter]
    except KeyError:
        print("No parameter '", parameter, "'in dictionary found")
        return ""

def main(argv):
    # constant variables
    fileExtension = ".json"
    apiEndpointURL = "https://returnyoutubedislikeapi.com/Votes"

    argument = parseArguments(argv)

    filenames = extractFiles(argument, fileExtension)

    print("File count:", len(filenames))

    for filename in filenames:
        with open(filename, 'r+') as file:
            print("file: '", filename, "'")
            try:
                file_dictionary = json.load(file)          
            except ValueError:
                print("Couldn't load following json file: '", filename, "'")
                continue
            ID = getVideoIDfromJson(file_dictionary, "id")
            response = apiGETRequest(apiEndpointURL, {"videoId": ID})
            if not response:
                continue
            dislikes = response["dislikes"]
            tmp = appendDataToJson(file_dictionary, "like_count", {"dislike_count":dislikes})
            file.seek(0)
            json.dump(tmp, file)

if __name__ == '__main__' :
    main(sys.argv[1:])
