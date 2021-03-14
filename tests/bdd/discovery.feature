Feature: Device discovery
  As a Web-API consumer
  I want to use the websocket connection
  So that I'll be notified about discovery events

  Scenario: New MediaServer advertised
    Given a client listens for discovery events
    When a MediaServer FooMediaServer appears on the network
    Then the client will be notified about the new FooMediaServer
    And  the media server FooMediaServer will be in the library API device list

  Scenario: New MediaRenderer advertised
    Given a client listens for discovery events
    When a MediaRenderer AcmeRenderer appears on the network
    Then the client will be notified about the new AcmeRenderer
    And  the media renderer AcmeRenderer will be in the player API device list

  Scenario: New Printer advertised
    Given a client listens for discovery events
    When a Printer BazPrinter appears on the network
    Then the client will receive no notification

  Scenario: MediaServer leaves
    Given a device FooMediaServer already present on the network
    And a client listens for discovery events
    When a MediaServer FooMediaServer leaves the network
    Then the client will be notified about the lost FooMediaServer
    And  the media server FooMediaServer will not be in the library API device list


