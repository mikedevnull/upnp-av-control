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

  Scenario: Playback is stopped at the end of the media item
    Given a device AcmeRenderer already present on the network
    And a device FooMediaServer already present on the network
    And a client subscribed to playback notifications from AcmeRenderer
    When the client requests to play item with id 0/2/2 from FooMediaServer on AcmeRenderer
    And the duration of item with id 0/2/2 from FooMediaServer has passed
    Then the client will be notified that AcmeRenderer is now in STOPPED state
    And the playback state reported by the API of AcmeRenderer is STOPPED
    And the device AcmeRenderer is playing item 0/2/2 from FooMediaServer
