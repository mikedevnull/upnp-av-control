Feature: Renderer state notifications
  As a Web-API client
  I want interact with the renderer
  So that I'll be notified about (playback) state changes

  Scenario: Client can query the initial volume
    Given a device AcmeRenderer already present on the network
    Then the volume reported by the API of AcmeRenderer is 42

  Scenario: Device volume changes are evented
    Given a device AcmeRenderer already present on the network
    And a client subscribed to playback notifications from AcmeRenderer
    When the playback volume of AcmeRenderer changes to 10
    Then the client will be notified about the new volume 10

  Scenario: Clients can change the volume
    Given a device AcmeRenderer already present on the network
    And a client subscribed to playback notifications from AcmeRenderer
    When the client requests to change the volume of AcmeRenderer to 32
    Then the client will be notified about the new volume 32
    And the volume reported by the API of AcmeRenderer is 32

  Scenario: Clients cannot change the volume to illegal values
    Given a device AcmeRenderer already present on the network
    When the client requests to change the volume of AcmeRenderer to 110
    Then the volume reported by the API of AcmeRenderer is 42

  Scenario: Clients cannot change the volume of an unkown device
    When the client requests to change the volume of an unkown device to 12
    Then an error has been reported

  Scenario: Clients cannot query the volume of an unkown device
    When the client requests the volume of an unkown device
    Then an error has been reported

  Scenario Outline: Device transport changes are evented
    Given a device AcmeRenderer already present on the network
    And a client subscribed to playback notifications from AcmeRenderer
    When the transport state of AcmeRenderer changes to <devicestate>
    Then the client will be notified about the new state <apistate>

    Examples:
      | devicestate     | apistate |
      | PLAYING         | PLAYING  |
      | PAUSED_PLAYBACK | PAUSED   |
