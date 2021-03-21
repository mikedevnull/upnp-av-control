Feature: Renderer state notifications
  As a Web-API client
  I want to subscribe to a renderer's events
  So that I'll be notified about (playback) state changes

  Scenario: Volume changes are evented
    Given a device AcmeRenderer already present on the network
    And a client subscribed to playback notifications from AcmeRenderer
    When the playback volume of AcmeRenderer changes to 10
    Then the client will be notified about the new volume 10

