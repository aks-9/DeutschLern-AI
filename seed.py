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
                content="<p>Placeholder</p>",
            ),
            GrammarTopic(
                order_index=2,
                title="Sein und Haben — To Be & To Have",
                level="A1",
                content="<p>Placeholder</p>",
            ),
            GrammarTopic(
                order_index=3,
                title="Grundlegende Satzstruktur — Basic Sentence Structure",
                level="A1",
                content="<p>Placeholder</p>",
            ),
            GrammarTopic(
                order_index=4,
                title="Zahlen und Zeit — Numbers & Time",
                level="A1",
                content="<p>Placeholder</p>",
            ),
            GrammarTopic(
                order_index=5,
                title="Begrüßungen — Greetings & Introductions",
                level="A1",
                content="<p>Placeholder</p>",
            ),
            GrammarTopic(
                order_index=6,
                title="Verben im Präsens — Present Tense Verbs",
                level="A1",
                content="<p>Placeholder</p>",
            ),
        ]

        session.add_all(topics)
        await session.commit()
        print("Seeded 6 AI grammar topics successfully")

if __name__ == "__main__":
    asyncio.run(seed())