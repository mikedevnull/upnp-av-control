Feature: Media server API
  As a Web-API client
  I want interact with the media server
  So i can browse the media library

  Scenario: Client can query object metadata
    Given a device FooMediaServer already present on the network
    When the client requests the object metadata of object SomeFakeObject on FooMediaServer
    Then the response will contain the metadata of object SomeFakeObject on FooMediaServer

  Scenario: Content browsing
    Given a device FooMediaServer already present on the network
    When the client requests the contents of the root element
    And the client requests link of the second item in the response
    Then the response will contain the content listing of this second item

  Scenario Outline: Pagination
    Given a device FooMediaServer already present on the network
    When the client requests page <pagenumber> with size <pagesize> of object FakeLongArtistListing
    Then the response will contain elements from index <first_element> to index <last_element>

    Examples:
      | pagenumber | pagesize | first_element | last_element |
      | 0          | 5        | 0             | 4            |
      | 3          | 3        | 9             | 11           |
      | 3          | 5        | 15            | 19           |
