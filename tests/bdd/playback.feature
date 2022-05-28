Feature: Playback
  As a Web-API client
  I want to use a MediaRenderer to play content from a MediaServer

  Scenario: Enqueue files for playback
    Given a device AcmeRenderer already present on the network
    And a device FooMediaServer already present on the network
    And a client subscribed to playback notifications from AcmeRenderer
    And the playback queue for AcmeRenderer is empty
    When the client adds item with id 0/2/2 from FooMediaServer to AcmeRenderer playback queue
    And the client adds item with id 0/1/1 from FooMediaServer to AcmeRenderer playback queue
    Then the playback queue of AcmeRenderer contains the following items:
      | item id | dms            |
      | 0/2/2   | FooMediaServer |
      | 0/1/1   | FooMediaServer |


  Scenario: Enqueue files and start playback
    Given a device AcmeRenderer already present on the network
    And a device FooMediaServer already present on the network
    And a client subscribed to playback notifications from AcmeRenderer
    And the playback queue for AcmeRenderer is empty
    When the client adds item with id 0/2/2 from FooMediaServer to AcmeRenderer playback queue
    And the client adds item with id 0/1/1 from FooMediaServer to AcmeRenderer playback queue
    And the client starts playback on AcmeRenderer
    Then the playback state reported by the API of AcmeRenderer is PLAYING
    And the device AcmeRenderer is playing item 0/2/2 from FooMediaServer
    And the playback queue of AcmeRenderer contains the following items:
      | item id | dms            |
      | 0/2/2   | FooMediaServer |
      | 0/1/1   | FooMediaServer |
    And the playback queue current item index of AcmeRenderer is 0

  Scenario: Replace contents of playback queue
    Given a device AcmeRenderer already present on the network
    And a device FooMediaServer already present on the network
    And a client subscribed to playback notifications from AcmeRenderer
    And the playback queue of AcmeRenderer already contains the following items:
      | item id | dms            |
      | 0/2/2   | FooMediaServer |
      | 0/1/1   | FooMediaServer |
    When the client replaces the content of the queue of AcmeRenderer with the following items:
      | item id | dms            |
      | 0/3/4   | FooMediaServer |
      | 0/7/8   | FooMediaServer |
      | 0/5/6   | FooMediaServer |
    Then the playback queue of AcmeRenderer contains the following items:
      | item id | dms            |
      | 0/3/4   | FooMediaServer |
      | 0/7/8   | FooMediaServer |
      | 0/5/6   | FooMediaServer |
    And the playback queue current item index of AcmeRenderer is not defined

  Scenario: Replace contents of playback queue with new item index
    Given a device AcmeRenderer already present on the network
    And a device FooMediaServer already present on the network
    And a client subscribed to playback notifications from AcmeRenderer
    And the playback queue of AcmeRenderer already contains the following items:
      | item id | dms            |
      | 0/2/2   | FooMediaServer |
      | 0/1/1   | FooMediaServer |
    When the client replaces the content of the queue of AcmeRenderer with the following items and current item index 2:
      | item id | dms            |
      | 0/3/4   | FooMediaServer |
      | 0/7/8   | FooMediaServer |
      | 0/5/6   | FooMediaServer |
    Then the playback queue of AcmeRenderer contains the following items:
      | item id | dms            |
      | 0/3/4   | FooMediaServer |
      | 0/7/8   | FooMediaServer |
      | 0/5/6   | FooMediaServer |
    And the playback queue current item index of AcmeRenderer is 2

  Scenario: Automatic playback of next item in queue
    Given a device AcmeRenderer already present on the network
    And a device FooMediaServer already present on the network
    And a client subscribed to playback notifications from AcmeRenderer
    And the playback queue of AcmeRenderer already contains the following items:
      | item id | dms            |
      | 0/2/2   | FooMediaServer |
      | 0/1/1   | FooMediaServer |
      | 0/3/4   | FooMediaServer |
      | 0/7/8   | FooMediaServer |
      | 0/5/6   | FooMediaServer |
    When the client starts playback on AcmeRenderer
    And AcmeRenderer finishes playback of current track
    Then the device AcmeRenderer is playing item 0/1/1 from FooMediaServer
    And the playback queue of AcmeRenderer contains the following items:
      | item id | dms            |
      | 0/2/2   | FooMediaServer |
      | 0/1/1   | FooMediaServer |
      | 0/3/4   | FooMediaServer |
      | 0/7/8   | FooMediaServer |
      | 0/5/6   | FooMediaServer |
    And the playback queue current item index of AcmeRenderer is 1

  Scenario: Playback stop after last item in queue
    Given a device AcmeRenderer already present on the network
    And a device FooMediaServer already present on the network
    And a client subscribed to playback notifications from AcmeRenderer
    And the playback queue of AcmeRenderer already contains the following items:
      | item id | dms            |
      | 0/7/8   | FooMediaServer |
      | 0/5/6   | FooMediaServer |
    When the client starts playback on AcmeRenderer
    And AcmeRenderer finishes playback of current track
    And the client read all pending notifications
    And AcmeRenderer finishes playback of current track
    Then the client will be notified that AcmeRenderer is now in STOPPED state
    And the playback state reported by the API of AcmeRenderer is STOPPED
    And the playback queue of AcmeRenderer contains the following items:
      | item id | dms            |
      | 0/7/8   | FooMediaServer |
      | 0/5/6   | FooMediaServer |
    And the playback queue current item index of AcmeRenderer is not defined


  Scenario: Independent playback queues
    Given a device AcmeRenderer already present on the network
    And a device PhonoRenderer already present on the network
    And a device FooMediaServer already present on the network
    When the client adds item with id 0/2/2 from FooMediaServer to PhonoRenderer playback queue
    And the client adds item with id 0/1/1 from FooMediaServer to PhonoRenderer playback queue
    Then the playback queue of PhonoRenderer contains the following items:
      | item id | dms            |
      | 0/2/2   | FooMediaServer |
      | 0/1/1   | FooMediaServer |
    And the playback queue of AcmeRenderer is empty


  Scenario: Change current playback item
    Given a device AcmeRenderer already present on the network
    And a device FooMediaServer already present on the network
    And a client subscribed to playback notifications from AcmeRenderer
    And the playback queue of AcmeRenderer already contains the following items:
      | item id | dms            |
      | 0/7/8   | FooMediaServer |
      | 0/5/6   | FooMediaServer |
    When the client starts playback on AcmeRenderer
    And the client read all pending notifications
    And the client sets the current queue item index of AcmeRenderer to 1
    Then the device AcmeRenderer is playing item 0/5/6 from FooMediaServer
    And the playback queue current item index of AcmeRenderer is 1

  Scenario: Stop playback with API
    Given a device AcmeRenderer already present on the network
    And a device FooMediaServer already present on the network
    And a client subscribed to playback notifications from AcmeRenderer
    And the playback queue of AcmeRenderer already contains the following items:
      | item id | dms            |
      | 0/7/8   | FooMediaServer |
      | 0/5/6   | FooMediaServer |
    And the state of AcmeRenderer is PLAYING
    And the client read all pending notifications
    When the client stops playback on AcmeRenderer
    Then the client will be notified that AcmeRenderer is now in STOPPED state
    And the playback state reported by the API of AcmeRenderer is STOPPED
    And the playback queue of AcmeRenderer contains the following items:
      | item id | dms            |
      | 0/7/8   | FooMediaServer |
      | 0/5/6   | FooMediaServer |
    And the playback queue current item index of AcmeRenderer is 0


