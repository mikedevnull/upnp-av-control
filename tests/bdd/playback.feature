Feature: Playback
  As a Web-API client
  I want to use a MediaRenderer to play content from a MediaServer

  Scenario: Start playback
    Given a device AcmeRenderer already present on the network
    And a device FooMediaServer already present on the network
    And a client subscribed to playback notifications from AcmeRenderer
    When the client requests to play item with id 0/2/2 from FooMediaServer on AcmeRenderer
    Then the client will be notified that AcmeRenderer is now in PLAYING state
    And the playback state reported by the API of AcmeRenderer is PLAYING
    And the device AcmeRenderer is playing item 0/2/2 from FooMediaServer
