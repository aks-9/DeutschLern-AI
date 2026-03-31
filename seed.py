import asyncio
from app.database import AsyncSessionLocal
from app.models import GrammarTopic
from sqlalchemy import select
async def seed():
    """Seed 6 AI grammar topics into the database"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(GrammarTopic))
        if result.scalars().first():
            print("Topics already seeded. Skipping.")
            return

        topics = [
            GrammarTopic(
                order_index=1,
                title="Der, Die, Das — German Articles",
                level="A1",
                content=(
                    "<h2>Der, Die, Das — German Articles</h2>"
                    "<p>Every German noun has a gender: "
                    "<strong>masculine</strong>, <strong>feminine</strong>, "
                    "or <strong>neuter</strong>. The definite article changes "
                    "depending on the gender.</p>"
                    "<table>"
                    "<thead><tr><th>Gender</th><th>Article</th>"
                    "<th>Example</th><th>Meaning</th></tr></thead>"
                    "<tbody>"
                    "<tr><td>Masculine</td><td><strong>der</strong></td>"
                    "<td>der Mann</td><td>the man</td></tr>"
                    "<tr><td>Feminine</td><td><strong>die</strong></td>"
                    "<td>die Frau</td><td>the woman</td></tr>"
                    "<tr><td>Neuter</td><td><strong>das</strong></td>"
                    "<td>das Kind</td><td>the child</td></tr>"
                    "<tr><td>Plural (all)</td><td><strong>die</strong></td>"
                    "<td>die Kinder</td><td>the children</td></tr>"
                    "</tbody></table>"
                    "<p><strong>Tip:</strong> Always learn the article with "
                    "the noun — e.g. <em>der Tisch</em>, not just "
                    "<em>Tisch</em>.</p>"
                ),
            ),
            GrammarTopic(
                order_index=2,
                title="Sein und Haben — To Be & To Have",
                level="A1",
                content=(
                    "<h2>Sein und Haben — To Be &amp; To Have</h2>"
                    "<p><strong>Sein</strong> (to be) and "
                    "<strong>haben</strong> (to have) are the two most "
                    "important verbs in German. Both are irregular.</p>"
                    "<h3>Sein — to be</h3>"
                    "<table>"
                    "<thead><tr><th>Pronoun</th><th>Verb</th>"
                    "<th>Meaning</th></tr></thead>"
                    "<tbody>"
                    "<tr><td>ich</td><td><strong>bin</strong></td>"
                    "<td>I am</td></tr>"
                    "<tr><td>du</td><td><strong>bist</strong></td>"
                    "<td>you are</td></tr>"
                    "<tr><td>er / sie / es</td><td><strong>ist</strong></td>"
                    "<td>he / she / it is</td></tr>"
                    "<tr><td>wir</td><td><strong>sind</strong></td>"
                    "<td>we are</td></tr>"
                    "<tr><td>ihr</td><td><strong>seid</strong></td>"
                    "<td>you (plural) are</td></tr>"
                    "<tr><td>sie / Sie</td><td><strong>sind</strong></td>"
                    "<td>they / you (formal) are</td></tr>"
                    "</tbody></table>"
                    "<h3>Haben — to have</h3>"
                    "<table>"
                    "<thead><tr><th>Pronoun</th><th>Verb</th>"
                    "<th>Meaning</th></tr></thead>"
                    "<tbody>"
                    "<tr><td>ich</td><td><strong>habe</strong></td>"
                    "<td>I have</td></tr>"
                    "<tr><td>du</td><td><strong>hast</strong></td>"
                    "<td>you have</td></tr>"
                    "<tr><td>er / sie / es</td><td><strong>hat</strong></td>"
                    "<td>he / she / it has</td></tr>"
                    "<tr><td>wir</td><td><strong>haben</strong></td>"
                    "<td>we have</td></tr>"
                    "<tr><td>ihr</td><td><strong>habt</strong></td>"
                    "<td>you (plural) have</td></tr>"
                    "<tr><td>sie / Sie</td><td><strong>haben</strong></td>"
                    "<td>they / you (formal) have</td></tr>"
                    "</tbody></table>"
                    "<p><strong>Examples:</strong> "
                    "<em>Ich bin Student.</em> — I am a student. "
                    "<em>Sie hat ein Buch.</em> — She has a book.</p>"
                ),
            ),
            GrammarTopic(
                order_index=3,
                title="Grundlegende Satzstruktur — Basic Sentence Structure",
                level="A1",
                content=(
                    "<h2>Grundlegende Satzstruktur — Basic Sentence "
                    "Structure</h2>"
                    "<p>In German, the verb <strong>always</strong> comes in "
                    "position 2 in a statement. This is called the "
                    "<strong>V2 rule</strong>.</p>"
                    "<h3>Subject — Verb — Object</h3>"
                    "<table>"
                    "<thead><tr><th>Position 1</th><th>Position 2 (Verb)"
                    "</th><th>Rest</th></tr></thead>"
                    "<tbody>"
                    "<tr><td>Ich</td><td><strong>lerne</strong></td>"
                    "<td>Deutsch.</td></tr>"
                    "<tr><td>Er</td><td><strong>kauft</strong></td>"
                    "<td>ein Buch.</td></tr>"
                    "<tr><td>Wir</td><td><strong>essen</strong></td>"
                    "<td>Pizza.</td></tr>"
                    "</tbody></table>"
                    "<h3>When something else starts the sentence</h3>"
                    "<p>If a time word or place comes first, the verb still "
                    "stays in position 2 and the subject moves after it.</p>"
                    "<table>"
                    "<thead><tr><th>Position 1</th><th>Position 2 (Verb)"
                    "</th><th>Subject</th><th>Rest</th></tr></thead>"
                    "<tbody>"
                    "<tr><td>Heute</td><td><strong>lerne</strong></td>"
                    "<td>ich</td><td>Deutsch.</td></tr>"
                    "<tr><td>In Berlin</td><td><strong>wohnt</strong></td>"
                    "<td>er</td><td>seit zwei Jahren.</td></tr>"
                    "</tbody></table>"
                    "<p><strong>Tip:</strong> Questions swap the subject and "
                    "verb: <em>Lernst du Deutsch?</em> — Are you learning "
                    "German?</p>"
                ),
            ),
            GrammarTopic(
                order_index=4,
                title="Zahlen und Zeit — Numbers & Time",
                level="A1",
                content=(
                    "<h2>Zahlen und Zeit — Numbers &amp; Time</h2>"
                    "<h3>Numbers 1–20</h3>"
                    "<table>"
                    "<thead><tr><th>Number</th><th>German</th>"
                    "<th>Number</th><th>German</th></tr></thead>"
                    "<tbody>"
                    "<tr><td>1</td><td>eins</td>"
                    "<td>11</td><td>elf</td></tr>"
                    "<tr><td>2</td><td>zwei</td>"
                    "<td>12</td><td>zwölf</td></tr>"
                    "<tr><td>3</td><td>drei</td>"
                    "<td>13</td><td>dreizehn</td></tr>"
                    "<tr><td>4</td><td>vier</td>"
                    "<td>14</td><td>vierzehn</td></tr>"
                    "<tr><td>5</td><td>fünf</td>"
                    "<td>15</td><td>fünfzehn</td></tr>"
                    "<tr><td>6</td><td>sechs</td>"
                    "<td>16</td><td>sechzehn</td></tr>"
                    "<tr><td>7</td><td>sieben</td>"
                    "<td>17</td><td>siebzehn</td></tr>"
                    "<tr><td>8</td><td>acht</td>"
                    "<td>18</td><td>achtzehn</td></tr>"
                    "<tr><td>9</td><td>neun</td>"
                    "<td>19</td><td>neunzehn</td></tr>"
                    "<tr><td>10</td><td>zehn</td>"
                    "<td>20</td><td>zwanzig</td></tr>"
                    "</tbody></table>"
                    "<h3>Tens</h3>"
                    "<p>30 — dreißig, 40 — vierzig, 50 — fünfzig, "
                    "60 — sechzig, 70 — siebzig, 80 — achtzig, "
                    "90 — neunzig, 100 — hundert</p>"
                    "<p><strong>Pattern:</strong> 21 = einundzwanzig "
                    "(one-and-twenty), 35 = fünfunddreißig.</p>"
                    "<h3>Telling the Time</h3>"
                    "<table>"
                    "<thead><tr><th>German</th><th>Meaning</th></tr></thead>"
                    "<tbody>"
                    "<tr><td>Es ist drei Uhr.</td>"
                    "<td>It is 3 o'clock.</td></tr>"
                    "<tr><td>Es ist halb vier.</td>"
                    "<td>It is half past three (3:30).</td></tr>"
                    "<tr><td>Es ist Viertel nach fünf.</td>"
                    "<td>It is quarter past five (5:15).</td></tr>"
                    "<tr><td>Es ist Viertel vor sechs.</td>"
                    "<td>It is quarter to six (5:45).</td></tr>"
                    "</tbody></table>"
                    "<h3>Days of the Week</h3>"
                    "<p>Montag, Dienstag, Mittwoch, Donnerstag, Freitag, "
                    "Samstag, Sonntag</p>"
                    "<h3>Months</h3>"
                    "<p>Januar, Februar, März, April, Mai, Juni, Juli, "
                    "August, September, Oktober, November, Dezember</p>"
                ),
            ),
            GrammarTopic(
                order_index=5,
                title="Begrüßungen — Greetings & Introductions",
                level="A1",
                content=(
                    "<h2>Begrüßungen — Greetings &amp; Introductions</h2>"
                    "<h3>Greetings</h3>"
                    "<table>"
                    "<thead><tr><th>German</th><th>Meaning</th>"
                    "<th>When to use</th></tr></thead>"
                    "<tbody>"
                    "<tr><td>Hallo</td><td>Hello</td>"
                    "<td>Informal, any time</td></tr>"
                    "<tr><td>Guten Morgen</td><td>Good morning</td>"
                    "<td>Until ~11:00</td></tr>"
                    "<tr><td>Guten Tag</td><td>Good day</td>"
                    "<td>Formal, daytime</td></tr>"
                    "<tr><td>Guten Abend</td><td>Good evening</td>"
                    "<td>From ~18:00</td></tr>"
                    "<tr><td>Tschüss</td><td>Bye</td>"
                    "<td>Informal</td></tr>"
                    "<tr><td>Auf Wiedersehen</td><td>Goodbye</td>"
                    "<td>Formal</td></tr>"
                    "<tr><td>Bis bald</td><td>See you soon</td>"
                    "<td>Informal</td></tr>"
                    "</tbody></table>"
                    "<h3>Introductions</h3>"
                    "<table>"
                    "<thead><tr><th>German</th><th>Meaning</th></tr></thead>"
                    "<tbody>"
                    "<tr><td>Ich heiße Anna.</td>"
                    "<td>My name is Anna.</td></tr>"
                    "<tr><td>Ich bin Anna.</td>"
                    "<td>I am Anna.</td></tr>"
                    "<tr><td>Wie heißen Sie?</td>"
                    "<td>What is your name? (formal)</td></tr>"
                    "<tr><td>Wie heißt du?</td>"
                    "<td>What is your name? (informal)</td></tr>"
                    "<tr><td>Woher kommen Sie?</td>"
                    "<td>Where are you from? (formal)</td></tr>"
                    "<tr><td>Ich komme aus England.</td>"
                    "<td>I am from England.</td></tr>"
                    "<tr><td>Wie geht es Ihnen?</td>"
                    "<td>How are you? (formal)</td></tr>"
                    "<tr><td>Wie geht's?</td>"
                    "<td>How are you? (informal)</td></tr>"
                    "<tr><td>Gut, danke!</td>"
                    "<td>Good, thank you!</td></tr>"
                    "</tbody></table>"
                ),
            ),
            GrammarTopic(
                order_index=6,
                title="Verben im Präsens — Present Tense Verbs",
                level="A1",
                content=(
                    "<h2>Verben im Präsens — Present Tense Verbs</h2>"
                    "<p>Regular German verbs follow a predictable pattern. "
                    "Take the infinitive, remove <strong>-en</strong>, and "
                    "add the correct ending.</p>"
                    "<h3>Conjugation Pattern</h3>"
                    "<table>"
                    "<thead><tr><th>Pronoun</th><th>Ending</th>"
                    "<th>machen</th><th>lernen</th></tr></thead>"
                    "<tbody>"
                    "<tr><td>ich</td><td><strong>-e</strong></td>"
                    "<td>mache</td><td>lerne</td></tr>"
                    "<tr><td>du</td><td><strong>-st</strong></td>"
                    "<td>machst</td><td>lernst</td></tr>"
                    "<tr><td>er / sie / es</td><td><strong>-t</strong></td>"
                    "<td>macht</td><td>lernt</td></tr>"
                    "<tr><td>wir</td><td><strong>-en</strong></td>"
                    "<td>machen</td><td>lernen</td></tr>"
                    "<tr><td>ihr</td><td><strong>-t</strong></td>"
                    "<td>macht</td><td>lernt</td></tr>"
                    "<tr><td>sie / Sie</td><td><strong>-en</strong></td>"
                    "<td>machen</td><td>lernen</td></tr>"
                    "</tbody></table>"
                    "<h3>Common Regular Verbs</h3>"
                    "<table>"
                    "<thead><tr><th>Infinitive</th>"
                    "<th>Meaning</th></tr></thead>"
                    "<tbody>"
                    "<tr><td>machen</td><td>to make / to do</td></tr>"
                    "<tr><td>spielen</td><td>to play</td></tr>"
                    "<tr><td>arbeiten</td><td>to work</td></tr>"
                    "<tr><td>lernen</td><td>to learn</td></tr>"
                    "<tr><td>kommen</td><td>to come</td></tr>"
                    "</tbody></table>"
                    "<p><strong>Note:</strong> Verbs ending in "
                    "<strong>-ten</strong> or <strong>-den</strong> (like "
                    "<em>arbeiten</em>) add an extra <strong>e</strong> "
                    "before the ending for easier pronunciation: "
                    "<em>du arbeitest</em>, <em>er arbeitet</em>.</p>"
                ),
            ),
        ]

        session.add_all(topics)
        await session.commit()
        print("Seeded 6 AI grammar topics successfully")

if __name__ == "__main__":
    asyncio.run(seed())