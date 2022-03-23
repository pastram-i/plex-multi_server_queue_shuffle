#Required packages
from plexapi.myplex import MyPlexAccount
from plexapi.utils import millisecondToHumanstr
from plexapi.client import PlexClient
from plexapi.exceptions import BadRequest
import config, random, re, time

myAccount = MyPlexAccount(config.username,config.password)
plextv_clients = [x for x in myAccount.resources() if "player" in x.provides and x.presence and x.publicAddressMatches]
myServers = [myAccount.resource(server).connect() for server in config.servers]

myShows = {}
myQueue = []

#Pulls shows from playlists on each server
for server in myServers:
    for playlist in server.playlists():
        for episode in playlist.items():
            if episode.grandparentTitle not in myShows.keys():
                myShows[episode.grandparentTitle] = [] #Will add all unique show names from all servers
            if episode not in myShows[episode.grandparentTitle]:
                myShows[episode.grandparentTitle].append(episode) #Will add all unique episodes from all servers

#Organizing shows by 's##e##' text at the end of the <Episode> object
for value in myShows.values():
    value.sort(key=lambda x: re.sub(r'Episode:.+?-s', '',str(x)))

#Adds a queue of 100 episodes to play
while len(myQueue) < 100:
    i=0
    toAdd = random.choice(list(myShows))
    for episode in myShows[toAdd]:
        if episode.viewCount <= i and episode not in myQueue:
            myQueue.append(episode)
            break
        else:
            i+=1
            continue

#Starts to play queue, using the PlexServer attribute in the Episode object
for playEpisode in myQueue:
    print(
        '''----------------------------
        Now playing:            {}
        Season:                 {}
        Episode:                {}
        Full Name:              {}
        Length (HH:MM:SS:MMMM): {}
        '''.format(playEpisode.grandparentTitle,playEpisode.parentTitle,playEpisode.title,str(playEpisode),millisecondToHumanstr(playEpisode.duration))
        )

    client = plextv_clients[0].connect()
    client.playMedia(playEpisode)

    time.sleep(playEpisode.duration/1000)
    while client.isPlayingMedia():
        time.sleep(10000)