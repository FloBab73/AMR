#import "../lib.typ": *

= Lorem Ipsum

== Lorem ipsum dolor

Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod
tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At
vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren,
no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit
amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut
labore et dolore magna aliquyam erat, sed diam voluptua.

== Lorem ipsum dolor

Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod
tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At
vero eos et accusam et justo duo dolores et ea rebum.

Verschiedene Zitierformen (entspricht den BibLaTeX-Befehlen):

- Standard-Zitat (numerisch): #cite(<Willberg2021>)
- Im Fließtext: #cite(<Willberg2021>, form: "prose")
- Als Fußnote: Text#footnote(cite(<Willberg2021>, form: "full"))
- Nur Autor: #cite(<Willberg2021>, form: "author")
- Nur Jahr: #cite(<Willberg2021>, form: "year")
- Vollständig: #cite(<Willberg2021>, form: "full")
