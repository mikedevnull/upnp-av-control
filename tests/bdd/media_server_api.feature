Feature: Library API
  As a Web-API client
  I want interact with the library API
  So i can browse the media server libraries

  Scenario: Media server as library root items
    Given a device FooMediaServer already present on the network
    When the client requests the contents of the root element
    Then the response will contain FooMediaServer as an entry

  Scenario: Content browsing
    Given a device FooMediaServer already present on the network
    When the client requests the contents of the root element
    And the client requests the contents of item Foo MediaServer
    Then the response will contain the content listing of the root item of FooMediaServer

  Scenario: Content browsing containers
    Given a device FooMediaServer already present on the network
    When the client requests the contents of the root element
    And the client requests the contents of item Foo MediaServer
    And the client requests the contents of item Music
    Then the response will contain the content listing of the Music item of FooMediaServer

  Scenario: Client can query object metadata
    Given a device FooMediaServer already present on the network
    When the client requests the contents of the root element
    And the client requests the contents of item Foo MediaServer
    And the client requests the contents of item Music
    And the client requests the metadata of item Song Title 1
    Then the response will contain the metadata of object Song Title 1 on FooMediaServer

  Scenario Outline: Pagination
    Given a device FooMediaServer already present on the network
    When the client requests the contents of the root element
    And the client requests the contents of item Foo MediaServer
    And the client requests the contents of item Music
    And the client requests page <pagenumber> with size <pagesize> of object FakeLongArtistListing
    Then the response will contain elements from index <first_element> to index <last_element>

    Examples:
      | pagenumber | pagesize | first_element | last_element |
      | 0          | 5        | 0             | 4            |
      | 3          | 3        | 9             | 11           |
      | 3          | 5        | 15            | 19           |
