#!/usr/bin/env python3

# simpleircbot.py - A simple IRC-bot written in python
#
# Copyright (C) 2015 : Niklas Hempel - http://liq-urt.de
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import re
import socket
import random

# --------------------------------------------- Start Settings ----------------------------------------------------
HOST = "irc.twitch.tv"                          # Hostname of the IRC-Server in this case twitch's
PORT = 6667                                     # Default IRC-Port
CHAN = "#ellegamee"                             # Channelname = #{Nickname}
NICK = "ellegame_bot"                           # Nickname = Twitch username
PASS = "oauth:im6hepggbnkei1di3jagxua9nxuemm"   # www.twitchapps.com/tmi/ # This is a temperary account/oauth made for this bot, use it if you want
MAXN = 6                                        # The max number that the player can guess from (also you need to add more gesses further down)
MAXU = 1000                                     # The max number of players in the roll dice list
# --------------------------------------------- End Settings -------------------------------------------------------

# --------------------------------------------- Global Variables Start ---------------------------------------------
dice_players = [] # Database for users in the dice game
data = "" # The buffer for the socket connection
# --------------------------------------------- Global Variables End -----------------------------------------------

# --------------------------------------------- Start Functions ----------------------------------------------------
def send_pong(msg):
    con.send(bytes('PONG %s\r\n' % msg, 'UTF-8'))

def send_message(chan, msg):
    con.send(bytes('PRIVMSG %s :%s\r\n' % (chan, msg), 'UTF-8'))

def send_nick(nick):
    con.send(bytes('NICK %s\r\n' % nick, 'UTF-8'))

def send_pass(password):
    con.send(bytes('PASS %s\r\n' % password, 'UTF-8'))

def join_channel(chan):
    con.send(bytes('JOIN %s\r\n' % chan, 'UTF-8'))

def part_channel(chan):
    con.send(bytes('PART %s\r\n' % chan, 'UTF-8'))
# --------------------------------------------- End Functions ------------------------------------------------------

# --------------------------------------------- Start Helper Functions ---------------------------------------------

def clear_list_if_needed():
    if len(dice_players) > MAXU:
        del dice_players[:]
        send_message(CHAN, 'To Bad, Reseting the game database')

def get_sender(msg):
    result = ""
    for char in msg:
        if char == "!":
            break
        if char != ":":
            result += char
    return result

def get_message(msg):
    result = ""
    i = 3
    length = len(msg)
    while i < length:
        result += msg[i] + " "
        i += 1
    result = result.lstrip(':')
    return result

def parse_message(msg, sender):
    if len(msg) >= 1:
        msg = msg.split(' ')
        if msg[0] in active_commands:
            active_commands[msg[0]](sender)
        elif msg[0].isdigit():
            print('THIS IS fun')
            if get_player_stats(sender) in dice_players:
                command_answer_role(sender, msg[0])

def randon_number():
    return random.randint(1,MAXN)

def get_player_stats(sender):
    player_stats = []
    for player in dice_players:
        if player[0] == sender:
            player_stats = player
            break
            break
    return player_stats

# --------------------------------------------- End Helper Functions -----------------------------------------------

# --------------------------------------------- Chat Commands Start ------------------------------------------------

def command_test(sender):
    send_message(CHAN, 'This is a test')

def command_quitrole(sender):
    stats = get_player_stats(sender)
    dice_players.remove(stats)

    send_message(CHAN, 'You have quit the game '+sender)

def command_asdf(sender):
    send_message(CHAN, 'asdfster')

def command_scylla126(sender):
    send_message(CHAN, 'He is the best! The one and only')
    
def command_answer_role(sender, number):

    stats = get_player_stats(sender)
    dice_players.remove(stats)
    stats[2] += 1
    dice_players.append(stats)

    if int(number) == int(stats[1]):
        dice_players.remove(stats)
        if stats[2] == 1:
            send_message(CHAN, 'You win '+sender+'!! You did it on your first try. The right answer was '+str(number))
        elif stats[2] == 2:
            send_message(CHAN, 'You win '+sender+'!! You did it on your second try. The right answer was '+str(number))
        elif stats[2] == 3:
            send_message(CHAN, 'You win '+sender+'!! You did it on your third try. The right answer was '+str(number))
        elif stats[2] == 4:
            send_message(CHAN, 'You win '+sender+'!! You did it on your fourth try. The right answer was '+str(number))
        elif stats[2] == 5:
            send_message(CHAN, 'You win '+sender+'!! You did it on your fifth try. The right answer was '+str(number))
        else:
            send_message(CHAN, 'You win '+sender+'!! You did it on your '+str(stats[2])+' th try. The right answer was '+str(number))
    else:
        send_message(CHAN, 'Wrong answer '+sender+', you have tried '+str(stats[2])+' try, try again')
    
def command_role(sender):
    if get_player_stats(sender) != []:
        send_message(CHAN, ('You are already in the game '+sender+'! Guess a number between 1 to '+str(MAXN)))
    else:
        dice_players.append([sender, randon_number(), 0])
        send_message(CHAN, (sender+', guess from 1 to '+str(MAXN)+'!'))

active_commands = {
    '!test': command_test,
    '!asdf': command_asdf,
    '!scylla126': command_scylla126,
    '!quit': command_quitrole,
    '!role': command_role
}

# --------------------------------------------- Chat Command End ----------------------------------------------

# --------------------------------------------- Main Loop Start ----------------------------------------------

con = socket.socket()
con.connect((HOST, PORT))

send_pass(PASS)
send_nick(NICK)
join_channel(CHAN)

while True:

    try:
        data = data+con.recv(1024).decode('UTF-8')
        data_split = re.split(r"[~\r\n]+", data)
        data = data_split.pop()

        for line in data_split:
            line = str.rstrip(line)
            line = str.split(line)

            if len(line) >= 1:
                if line[0] == 'PING':
                    send_pong(line[1])

                if line[1] == 'PRIVMSG':
                    sender = get_sender(line[0])
                    message = get_message(line)
                    parse_message(message, sender)

                    print(sender + ": " + message)

            clear_list_if_needed() # Checks is the list of players in the game is to big and then clears it to same space

    except socket.error:
        print("Socket died")

    except socket.timeout:
        print("Socket timeout")

# --------------------------------------------- Main Loop End ----------------------------------------------