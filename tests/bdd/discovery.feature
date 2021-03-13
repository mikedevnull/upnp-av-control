Feature: Device discovery
  As a Web-API consumer
  I want to use the websocket connection
  So that I'll be notified about discovery events

  Scenario: New MediaServer advertised
    Given a client listens for discovery events

    When a MediaServer appears on the network

    Then the client will receive a notification


