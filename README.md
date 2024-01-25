# translate-smsdb

This is a tool that takes in an sms.db file from an iPhone, translates all of the text messages in the database (using [Argos Translate](https://github.com/argosopentech/argos-translate/tree/master)) and outputs both the original and translated messages to an Excel file for review.  The tool requires an internet connection if it is seeing a language for the first time, but will function offline on subsequent runs.

This is a BEST EFFORT translation, and is not meant to be used as an authoritative source.  Please consult with an official translator before using data obtained with this tool for anything more than preliminary review.

## Usage

If attempting to translate a language for the first time, the computer running the tool must be connected to the internet, and the `--online` flag must be passed.

```bash
usage: translate-smsdb [-h] [-d DATABASE] [-f FROMCODE] [-o OUTPUT] [-t TOCODE] [--online ONLINE]

options:
  -h, --help            show this help message and exit
  -d DATABASE, --database DATABASE
                        Path to the SMS DB file to translate
  -f FROMCODE, --from FROMCODE
                        Two digit code of the language to translate from. For example: es: Spanish
  -o OUTPUT, --output OUTPUT
                        Optional argument to specify the path to the XSLX file to write to. Defaults to "output.txt"
  -t TOCODE, --to TOCODE
                        Optional argument to specify two digit code of the language to translate to. Default is English "en"
  --online ONLINE       Attempt to download new language packages. If not passed, program will attempt to use the offline cache.
```

## Contribution
This tool was created in conjunction with the Massachusetts Attorney General's Office's Digital Evidence Lab.  Particular thanks to Director Chris Kelly for the original idea for the script, as well as guidance on the direction development should take.
