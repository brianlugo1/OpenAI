import os
from ai import ai
from queries import *
from usage import usage
from details import details
from colorama import init, Fore
from Levenshtein import distance
from dotenv import load_dotenv
load_dotenv()

import readline



GPT = "chatgpt"
GPT_LEN = len(GPT)
PER = "perplexity"
PER_LEN = len(PER)
LMA = "llama"
LMA_LEN = len(LMA)
DTS = "details"
DTS_LEN = len(DTS)


def print_welcome_message():
    print(f"{Fore.CYAN}")
    print("------------------------------------------------")
    print("|         Welcome to AIConnector               |")
    print("|                                              |")
    print("|   I was created to help you connect with     |")
    print("|     ChatGPT or Perplexity and provide        |")
    print("|      insightful analytics about your         |")
    print("|               conversations!                 |")
    print("|                                              |")
    print("|   To ask ChatGPT a question simply type:     |")
    print(f"|       {GPT} or c                           |")
    print("|                                              |")
    print("|   To ask Perplexity a question simply type:  |")
    print(f"|       {PER} or p                        |")
    print("|                                              |")
    print("|   To ask Llama a question simply type:       |")
    print(f"|       {LMA} or l                             |")
    print("|                                              |")
    print("|   To view a detailed report type:            |")
    print(f"|       {DTS} or d                           |")
    print("|                                              |")
    print("|   To ask for help type:                      |")
    print("|       help or h                              |")
    print("|                                              |")
    print("------------------------------------------------")
    print()


def setup():
    init()

    conn, cur = create_connection()

    if conn == None and cur == None:
        return None, None

    create_table(conn, cur)

    os.system("clear")

    print_welcome_message()

    return conn, cur


def split_cmd(cmds):
    if cmds.find("&&") != -1:
        cmds=cmds.replace("&&", ";")

    return cmds.split(";")


def process_ai_cmd(conn, cur, msg, ai_cmd):
    if msg=="":
        usage(m="o", ai=ai_cmd)
        return

    ai(ai_cmd, conn, cur, msg.strip())


def process_details_cmd(cur, cmd):
    if cmd=="":
        usage(m="d")
        return

    if cmd.isnumeric():
        details(cur, cmd)
        return

    processed_cmd=cmd.split(" ")[0].lower()

    if len(processed_cmd) == 1:
        stored_cmds=[
            "t",
            "y",
            "a",
            "m",
            "l",
            "s",
            "d",
        ]

        for s_cmd in stored_cmds:
            if distance(s_cmd, processed_cmd) == 0:
                details(cur, cmd)
                return

        usage(m="d")

    else:
        stored_cmds=[
            "today",
            "yesterday",
            "all",
            "most",
            "longest",
            "shortest",
            "date",
        ]

        min_dist=4
        process_d_cmd=""

        for s_cmd in stored_cmds:
            dist=distance(cmd, s_cmd)

            if dist <= min_dist:
                min_dist=dist
                process_d_cmd=s_cmd

        if min_dist == 0:
            if processed_cmd == "date":
                processed_cmd=processed_cmd[:len(processed_cmd)]
                processed_cmd="d" + processed_cmd
                details(cur, processed_cmd)
                return

            details(cur, processed_cmd[:1])
            return

        if min_dist < 4:
            usage(m="p", probable_cmd=f"{process_d_cmd}")
            return

        usage(m="d")
        return


def exec_cmd(conn, cur, cmds):
    e=0

    stored_cmds=[
        "exit",
        "help",
        "clear",
        GPT,
        PER,
        DTS,
        LMA
    ]

    for cmd in cmds:
        cmd=cmd.strip()

        processed_cmd=cmd.split(" ")[0].lower()

        if processed_cmd=="":
            continue
        elif processed_cmd=="h":
            usage(m="h")
            continue
        elif processed_cmd=="c":
            process_ai_cmd(conn, cur, cmd[1:].strip(), GPT)
            continue
        elif processed_cmd=="p":
            process_ai_cmd(conn, cur, cmd[1:].strip(), PER)
            continue
        elif processed_cmd=="l":
            process_ai_cmd(conn, cur, cmd[1:].strip(), LMA)
            continue
        elif processed_cmd=="d":
            process_details_cmd(cur, cmd[1:].strip())
            continue
        elif processed_cmd=="cd":
            try:
                os.chdir(cmd[3:].strip())
                continue
            except:
                usage(m="f", f_n_f=cmd[3:].strip())
                continue
        elif processed_cmd=="ls":
            os.system("ls")
            continue
        elif processed_cmd=="pwd":
            os.system("pwd")
            continue

        if len(processed_cmd) < 4:
            usage(m="", cmd_n_f=processed_cmd)
            break

        min_dist=4
        probable_cmd=""

        for s_cmd in stored_cmds:
            dist=distance(processed_cmd, s_cmd)

            if dist <= min_dist:
                min_dist=dist
                probable_cmd=s_cmd

        if probable_cmd=="exit" and min_dist==0:
            e=1
            break

        if min_dist==0:
            if probable_cmd=="clear":
                os.system("clear")
            elif probable_cmd=="help":
                usage(m="h")
            elif probable_cmd==GPT:
                process_ai_cmd(conn, cur, cmd[GPT_LEN:].strip(), GPT)
            elif probable_cmd==PER:
                process_ai_cmd(conn, cur, cmd[PER_LEN:].strip(), PER)
            elif probable_cmd==LMA:
                process_ai_cmd(conn, cur, cmd[LMA_LEN:].strip(), LMA)
            elif probable_cmd==DTS:
                process_details_cmd(cur, cmd[DTS_LEN:].strip())
        elif min_dist==4:
            usage(m="", cmd_n_f=f"{processed_cmd}")
        else:
            usage(m="p", probable_cmd=f"{probable_cmd}")

    if e:
        usage(m="e")

    return e


def aicp():
    conn, cur=setup()

    if conn == None and cur == None:
        print("An error occurred connecting to the PostgreSQL server. Is the PostgreSQL server running?")
        return

    while True:
        cmds=str(input(f"{Fore.BLUE}aicp{Fore.CYAN}$ {Fore.WHITE}"))

        cmds=split_cmd(cmds)

        if exec_cmd(conn, cur, cmds):
            break


class MyCompleter(object):
    def __init__(self, options):
        self.options = sorted(options)

    def complete(self, text, state):
        if state == 0:
            line=readline.get_line_buffer()
            cmds=line.replace("&&", ";").split(";")
            tokens=cmds[-1].strip().split(" ")

            stored_cmds=[
                "exit",
                "help",
                "clear",
                GPT,
                PER,
                DTS,
                LMA
            ]

            stored_flags={
                DTS: [
                    "today",
                    "yesterday",
                    "all",
                    "most",
                    "longest",
                    "shortest",
                    "date",
                ]
            }

            cmd=tokens[0].strip().lower()

            if len(tokens) == 1:
                self.matches = [s for s in stored_cmds if s and s.startswith(cmd)]

            elif len(tokens) == 2:
                if cmd != DTS and cmd != "d":
                    return None

                flag=tokens[1].strip().lower()

                self.matches = [s for s in stored_flags[DTS] if s and s.startswith(flag)]

            if not text:
                self.matches = self.options[:]

        try:
            return self.matches[state]

        except IndexError:
            return None


readline.set_completer(MyCompleter([]).complete)
readline.parse_and_bind("tab: complete")
readline.parse_and_bind("bind ^I rl_complete")

aicp()