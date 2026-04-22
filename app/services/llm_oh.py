######################################################################################
## This will contain all the output handling functions, they can be moved to a      ##
## more appropriate file or just imported, this file does nothing on its own        ##
##                                                                                  ##
## some functionality may not be needed or may need to be adjusted so review is     ##
## probably needed; suggestions appreciated on what could be scrapped or edited     ##
##                                                                                  ##
## work done by Harry                                                               ##
######################################################################################

# array of words that probably shouldn't be printed and explanations
# additionally, phrases could be added if something keeps appearing during testing
# that we dont like
# could be improved by replacing with regex
avoid_words = [
    " shit", # I feel these words are self explanatory
    " fuck",
    " piss", # although i presonally think they could be removed as
    " crap", # they'd never be returned by an ai as it'd have its own handling

    " bomb", # might be returned if a user asks about what might cause seismic activity
    " nuclear bomb" # could be helpful or make the prompting a little fear mongering
]

def check_appropriate(response):
    # Checks if the response contains anything inapproriate
    # input: response(string, assumed)
    # output: bool(true for passing, false for contains bad language)

    passing = True # assume its the cleaning done by the api is sufficient
    for phrase in avoid_words:
        if phrase in response:
            passing = False
    
    return passing

def formatting(response):
    # appends a prespiel and post spiel to a response
    # input: response(string, assumed)
    # output: output(string, spiel)

    # Examples; these can be changed
    pre_spiel = "No problem, here's the answer to your question: "
    #default_prompt_pre_spiel = "Here's a brief overlook on the graphs you created, hope this helps: "

    post_spiel = "Did this help? Feel free to create more graphs, or ask more!"
    #default_prompt_pre_spiel = "Did the brief description help? Ask for specifics or clarification if needed!"

    # Example output; formatting could be different
    return pre_spiel + "\n\n" + response + "\n\n" + post_spiel

def main_flow(response):
    ## an idea of how the functions could be implemented into llm.py or similar file
    ## input: response(string, assumed)
    ## output:
    
    # clean the response
    valid = check_appropriate(response)

    # reprompt if inappropriate, or no response
    if (not valid) or (response == "No response generated."):
        # reprompt
        pass

    # return the formatted response for displaying
    return formatting(response)