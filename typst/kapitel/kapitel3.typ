#import "../lib.typ": *

= Lorem Ipsum

== Lorem ipsum dolor

Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod
tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At
vero eos et accusam et justo duo dolores et ea rebum.

== Lorem ipsum dolor

Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod
tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.

#bild("bilder/kapitel3/nasa_rover.jpg", 6cm, [Ein Nasa Rover], label: <Kap2:NasaRover>)

== Formelsatz

Eine Formel gefällig? Mitten im Text $a_2 = sqrt(x^3)$ oder als eigener Absatz
(siehe @Formel):

$
mat(1, 4, 2; 4, 0, -3)
dot
mat(1, 1, 0; -2, 3, 5; 0, 1, 4)
=
mat(-7, 15, 28; 4, 1, -12)
$ <Formel>

=== Lorem Ipsum

#listing(
  caption: [Methode checkKey()],
  ```java
  /**
   * Testet den Schlüssel auf Korrektheit: Er muss mindestens die Länge 1
   * haben und darf nur Zeichen von A-Z enthalten.
   *
   * @param key zu testender Schlüssel
   * @throws CrypterException wenn der Schlüssel nicht OK ist.
   */
  protected void checkKey(Key key) throws CrypterException {

      // Passt die Länge?
      if (key.getKey().length == 0) {
          throw new CrypterException("Der Schlüssel muss mindestens " +
                  "ein Zeichen lang sein");
      }

      checkCharacters(key.getKey(), ALPHABET);
  }
  ```,
)
