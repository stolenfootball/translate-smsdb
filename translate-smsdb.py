import argparse
import pathlib

import sqlite3
import pandas as pd

import argostranslate.package
import argostranslate.translate


COLUMNS_TO_RETRIEVE = [
    "chat_identifier",
    "service_name",
    "account_login",
    "last_addressed_handle",
    "last_read_message_timestamp",
    "text",
    "account",
    "date",
    "date_read",
    "cache_has_attachments",
    "destination_caller_id"
]

QUERY = f"""
SELECT {', '.join(column for column in COLUMNS_TO_RETRIEVE)} 
FROM chat
INNER JOIN chat_message_join ON chat_message_join.chat_id = chat.ROWID
INNER JOIN message ON message.ROWID = chat_message_join.message_id;
"""


def readDatabase(to_read: str) -> pd.DataFrame:
    """
    Takes a path (relative or absolute) to an Apple sms.db file, and returns all message and chat
    information held in columns indicated by the COLUMNS_TO_RETRIEVE list above.

    :param to_read: The path to the file to read

    :return: A Pandas dataframe with the returned SQL Query information in it.
    """

    if not to_read.is_file():
        raise Exception(f"Could not find database at path: {to_read.resolve()}")
    
    print("Reading database...")
    con = sqlite3.connect(to_read.resolve())

    try:
        df = pd.DataFrame(pd.read_sql(QUERY, con))
    except:
        raise Exception(f"SQL execution failed on file {to_read.resolve()}")
    
    con.close()
    return df


def downloadTranslationPackage(from_code: str, to_code: str, online: bool) -> None:
    """
    Retrieve the correct Argostranslate package for the codes specified and cache it.  Do not go online to 
    retrieve the packages unless specifically indicated by the online flag.

    :param from_code: Two digit country code specifying the native language of the sms.db file
    :param to_code: Two digit country code specifying the language to translate the messages to
    :param online:  Used as a flag - if truthy, goes online for translation packages.  
    """

    print("Locating translation package... ")
    try:
        if (online): argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()
        package_to_install = next(
            filter(
                lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
            )
        )
        print(f"Package for {package_to_install} located!")

    except StopIteration:
        raise Exception(f"Translation package for {from_code} to {to_code} could not be located.")
    
    argostranslate.package.install_from_path(package_to_install.download())


def translateAndUpdateDataframe(df: pd.DataFrame, from_code: str, to_code: str) -> None:
    """
    Take in a dataframe generated by parsing an sms.db file and translate it to the requested language.
    Add the translation in a new column next to the original text in the dataframe.

    :param df: Pandas dataframe containing the original sms.db information
    :param from_code: Two digit country code specifying the native language of the sms.db file
    :param to_code: Two digit country code specifying the language to translate the messages to
    """

    translated = []
    for index, row in df.iterrows():
        print(f"Translating: {index + 1} / {df.shape[0]} -> {int((index + 1) / df.shape[0] * 100)}%", end='\r')
        translated.append(argostranslate.translate.translate(row['text'], from_code, to_code)) if row['text'] else translated.append('')

    print()
    df.insert(df.columns.get_loc('text') + 1, "translated_text", translated, True)


def writeToExcel(df: pd.DataFrame, output_file='output.xlsx') -> None:
    """
    Write the Pandas dataframe to an Excel workbook for review.

    :param df: The Pandas dataframe to write to the workbook.
    :param output_file: The name of the output file to write to.
    """
    
    print("Writing to Excel...")
    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Translation')
    writer.close()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="translate-smsdb",
                                     description="A program to take an SMS DB and translate the messages to a language of choice.  Exports an Excel file.")
    parser.add_argument("-d", "--database", help="Path to the SMS DB file to translate")
    parser.add_argument("-f", "--from", dest='fromcode', help="Two digit code of the language to translate from.  For example: es: Spanish")
    parser.add_argument("-o", "--output", help="Optional argument to specify the path to the XSLX file to write to.  Defaults to \"output.txt\"",
                                          default="output.xlsx")
    parser.add_argument("-t", "--to", dest='tocode', help="Optional argument to specify two digit code of the language to translate to.  Default is English \"en\"",
                                default="en")
    parser.add_argument("--online", help="Attempt to download new language packages.  If not passed, program will attempt to use the offline cache.")
    args = parser.parse_args()

    try:
        df = readDatabase(pathlib.Path(args.database))
        downloadTranslationPackage(args.fromcode, args.tocode, args.online)
        translateAndUpdateDataframe(df, args.fromcode, args.tocode)
        writeToExcel(df)
    except Exception as e:
        print(f"[-] ERROR: {e}")