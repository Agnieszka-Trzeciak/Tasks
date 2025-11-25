import re

with open('task1_d.json') as f:
    contents = f.readlines()[0] # Read the file in
    contents = re.sub(r':([\w|\[|\]]+)\=\>',r'"\1":',contents) # Change all the :NAME=> into "NAME":
    contents = re.sub(r'}, ',r'},\n',contents) # Add end of lines for better readability
    with open('task1_d_processed.json', 'w') as output: # Save processed file
        output.write(contents)

