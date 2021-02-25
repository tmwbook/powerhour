import React, { Dispatch, useEffect, useState } from 'react';
import logo from './logo.svg';
import './site.css';
import axios from 'axios';
import { Button, Card, Column, Columns, Container, Content, Image, Media } from "trunx";

const authed_axios = axios.create({
  withCredentials: true
})

interface Playlist {
  collaberative: boolean,
  description: string,
  external_urls: any,
  href: string,
  id: string,
  images: any[],
  name: string,
  owner: any,
  primary_color: string | null,
  public: boolean,
  tracks: any,
  type: string,
  uri: string
}

function App() {

  const [loggedIn, setLoggedIn] = useState(false);
  const [authURL, setAuthURL] = useState("");
  const [playlists, setPlaylists]: [Playlist[], Dispatch<any>] = useState([]);

  const get_auth_url = function () {
    return axios.get("/get_auth_url")
    .then((resp) => {
      return (resp.data.url)
    })
  }

  const get_playlists = function () {
    authed_axios.get("/playlists")
    .then(json => {
      setPlaylists(json.data.items)
    })
  }

  const play_playlist = function (playlist_id:string) {
    authed_axios.post("/test_playlist", {playlist_id: playlist_id})
  }

  useEffect(() => {
    authed_axios.get("/check_auth")
    .then((resp) => {
      setLoggedIn(resp.status === 200)
    })
    get_auth_url()
    .then(url => setAuthURL(url))
  }, [])

  return (
    <div className="App">
        <Container>
        {
          loggedIn ?
          <Button onClick={get_playlists}>Get Playlists</Button>
          :
          <a href={authURL}>
            <Button>Login with Spotify</Button>
          </a>
        }</Container>
        <Container>
          <Columns className="is-multiline">
          { playlists.map((playlist: Playlist) => 
            <Column className="is-one-third" key={playlist.id}>
              <Card>
                <Card.Content>
                  <Media>
                  <Image src={playlist.images[0].url}></Image>
                  </Media>
                  <Content className="title is-4">{playlist.name}</Content>
                  {false && playlist.description.replace("&#x27;", "'")}
                </Card.Content>
                <Card.Footer isSize4>
                  <Card.Footer.Item onClick={() => {
                    play_playlist(playlist.uri)
                  }}>
                    Play Now
                  </Card.Footer.Item>
                  <Card.Footer.Item>
                    Schedule
                  </Card.Footer.Item>
                </Card.Footer>
              </Card>
            </Column>)
          }
          </Columns>
        </Container>
    </div>
  );
}

export default App;
