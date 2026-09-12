"""
Seed the PCA database with sample data.

Run:
    python seed.py
"""

import asyncio
from datetime import datetime, timedelta, timezone

from database.session import AsyncSessionLocal, create_tables
from models.user import User
from models.sender import Sender
from models.message import Message
from models.memory import Memory


async def seed():
    await create_tables()

    async with AsyncSessionLocal() as db:

        # -------------------------
        # Clear existing data
        # -------------------------

        await db.execute(Message.__table__.delete())
        await db.execute(Memory.__table__.delete())
        await db.execute(Sender.__table__.delete())
        await db.execute(User.__table__.delete())

        # -------------------------
        # User
        # -------------------------

        user = User(
            name="Demo User",
            preferred_language="en",
        )

        db.add(user)
        await db.flush()
        now = datetime.now(timezone.utc)

        # -------------------------
        # Senders
        # -------------------------

        professor = Sender(
            name="Professor",
            category="Education",
            default_language="en",
            avatar=None,
            profile_info={
                "role": "Faculty",
                "priority": "high",
            },
        )

        mother = Sender(
            name="Mother",
            category="Family",
            default_language="te",
            avatar=None,
            profile_info={
                "relationship": "Mother",
            },
        )

        ravi = Sender(
            name="Ravi",
            category="Friend",
            default_language="en",
            avatar=None,
            profile_info={
                "relationship": "College Friend",
            },
        )

        amazon = Sender(
            name="Amazon",
            category="Shopping",
            default_language="en",
            avatar=None,
            profile_info={
                "type": "E-commerce",
            },
        )

        bank = Sender(
            name="Bank",
            category="Finance",
            default_language="en",
            avatar=None,
            profile_info={
                "type": "Bank",
            },
        )

        ananya = Sender(
            name="Ananya",
            category="Friend",
            default_language="en",
            avatar=None,
            profile_info={
                "relationship": "Classmate",
            },
        )

        college = Sender(
            name="College",
            category="Education",
            default_language="en",
            avatar=None,
            profile_info={
                "institution": "MIC College of Technology",
            },
        )

        arjun = Sender(
            name="Arjun",
            category="Friend",
            default_language="en",
            avatar=None,
            profile_info={
                "relationship": "Friend",
            },
        )

        db.add_all([
            professor,
            mother,
            ravi,
            amazon,
            bank,
            ananya,
            college,
            arjun,
        ])

        await db.flush()

        # -------------------------
        # Memory
        # -------------------------

        db.add_all([

            Memory(
                sender_id=professor.id,
                summary="Professor teaches AIML courses and usually sends assignment deadlines and project updates.",
                key_facts={
                    "role": "Professor",
                    "priority": "High",
                    "reply_style": "Formal"
                },
                pending_actions=[
                    "Submit Assignment 5"
                ],
                last_interaction=now - timedelta(days=2),
            ),

            Memory(
                sender_id=mother.id,
                summary="Mother prefers communicating in Telugu and often asks about meals and arrival times.",
                key_facts={
                    "preferred_language": "te",
                    "relationship": "Mother"
                },
                pending_actions=[],
                last_interaction=now - timedelta(hours=12),
            ),

            Memory(
                sender_id=ravi.id,
                summary="College friend and hackathon teammate.",
                key_facts={
                    "relationship": "Friend",
                    "interests": [
                        "Hackathons",
                        "Gaming"
                    ]
                },
                pending_actions=[
                    "Confirm hackathon travel"
                ],
                last_interaction=now - timedelta(days=1),
            ),

            Memory(
                sender_id=ananya.id,
                summary="Classmate who frequently asks for lecture notes and assignment help.",
                key_facts={
                    "relationship": "Classmate",
                    "department": "AIML"
                },
                pending_actions=[
                    "Send today's lecture notes"
                ],
                last_interaction=now - timedelta(days=3),
            ),

            Memory(
                sender_id=arjun.id,
                summary="Friend who usually discusses games and weekend plans.",
                key_facts={
                    "relationship": "Friend",
                    "favorite_game": "Apex Legends"
                },
                pending_actions=[],
                last_interaction=now - timedelta(days=4),
            ),

        ])

        # -------------------------
        # Messages
        # -------------------------

        

        messages = [

            # Professor
            Message(
                sender_id=professor.id,
                text="Please submit Assignment 5 before tomorrow 5 PM.",
                language="en",
                timestamp=now - timedelta(hours=6),
                is_from_user=False,
                is_read=False,
                is_replied=False,
            ),

            # Mother
            Message(
                sender_id=mother.id,
                text="ఈ రోజు ఇంటికి ఎప్పుడు వస్తావు?",
                language="te",
                timestamp=now - timedelta(hours=5),
                is_from_user=False,
                is_read=False,
                is_replied=False,
            ),

            # Ravi
            Message(
                sender_id=ravi.id,
                text="Bro, are we leaving together for the hackathon tomorrow?",
                language="en",
                timestamp=now - timedelta(hours=4),
                is_from_user=False,
                is_read=False,
                is_replied=False,
            ),

            # Amazon
            Message(
                sender_id=amazon.id,
                text="Your HP Victus laptop stand has been shipped and will arrive tomorrow.",
                language="en",
                timestamp=now - timedelta(hours=3),
                is_from_user=False,
                is_read=False,
                is_replied=False,
            ),

            # Bank
            Message(
                sender_id=bank.id,
                text="₹25,000 has been credited to your savings account.",
                language="en",
                timestamp=now - timedelta(hours=2),
                is_from_user=False,
                is_read=False,
                is_replied=False,
            ),

            # Ananya
            Message(
                sender_id=ananya.id,
                text="Can you send me today's AIML lecture notes?",
                language="en",
                timestamp=now - timedelta(minutes=90),
                is_from_user=False,
                is_read=False,
                is_replied=False,
            ),

            # College
            Message(
                sender_id=college.id,
                text="Tomorrow's regular classes are suspended for students attending the VIT-AP Hackathon.",
                language="en",
                timestamp=now - timedelta(minutes=45),
                is_from_user=False,
                is_read=False,
                is_replied=False,
            ),

            # Arjun
            Message(
                sender_id=arjun.id,
                text="Want to play Apex Legends tonight after we're done coding?",
                language="en",
                timestamp=now - timedelta(minutes=15),
                is_from_user=False,
                is_read=False,
                is_replied=False,
            ),

        ]

        db.add_all(messages)

        await db.commit()

        print("======================================")
        print("PCA database seeded successfully!")
        print("======================================")
        print(f"User: {user.name}")
        print(f"Senders: {8}")
        print(f"Messages: {len(messages)}")
        print(f"Memory Records: {5}")
        print("======================================")


if __name__ == "__main__":
    asyncio.run(seed())