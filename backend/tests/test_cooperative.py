import unittest
from datetime import datetime

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.cooperative import create_insight, list_insights, reuse_insight
from app.database import Base
from app.main import reuse_cooperative_insight
from app.models import CooperativeInsight
from app.schemas import CooperativeInsightReuse


class CooperativeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine)

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()

    def publish(self, **overrides: object) -> CooperativeInsight:
        values = {
            "publisher_state": "Maharashtra",
            "crop": "Soybean",
            "insight_type": "advisory",
            "title": "Demo insight",
            "description": "Prototype description",
            "version": "v1",
            "metric_label": "score",
            "metric_value": 2,
        }
        values.update(overrides)
        return create_insight(self.session, **values)

    def test_publish_and_list(self) -> None:
        insight = self.publish()
        self.assertEqual(list_insights(self.session)[0].id, insight.id)

    def test_filters(self) -> None:
        self.publish()
        self.publish(publisher_state="Gujarat", crop="Pearl millet", insight_type="vegetation")
        self.assertEqual(len(list_insights(self.session, state="Gujarat")), 1)
        self.assertEqual(len(list_insights(self.session, crop="Soybean")), 1)
        self.assertEqual(len(list_insights(self.session, insight_type="vegetation")), 1)

    def test_reuse_creates_new_linked_record_without_mutating_source(self) -> None:
        source = self.publish()
        adapted = reuse_insight(
            self.session,
            source,
            target_state="Gujarat",
            adaptation_note="Adjusted for local conditions.",
        )
        self.assertNotEqual(adapted.id, source.id)
        self.assertEqual(adapted.source_insight_id, source.id)
        self.assertEqual(adapted.publisher_state, "Gujarat")
        self.assertEqual(adapted.status, "adapted")
        self.assertEqual(adapted.adaptation_note, "Adjusted for local conditions.")
        self.session.refresh(source)
        self.assertEqual(source.status, "published")
        self.assertIsNone(source.source_insight_id)
        self.assertIsNone(source.adaptation_note)

    def test_seed_shape_would_not_duplicate(self) -> None:
        self.publish()
        self.assertEqual(self.session.scalar(select(CooperativeInsight.id).limit(1)), 1)
        self.assertEqual(len(list_insights(self.session)), 1)

    def test_created_at_is_set(self) -> None:
        insight = self.publish()
        self.assertIsInstance(insight.created_at, datetime)

    def test_invalid_source_returns_not_found(self) -> None:
        class MissingSession:
            def get(self, *args: object) -> None:
                return None if args else None

        with self.assertRaisesRegex(Exception, "Cooperative insight not found"):
            reuse_cooperative_insight(
                999,
                CooperativeInsightReuse(
                    target_state="Gujarat",
                    adaptation_note="Demo adaptation",
                ),
                MissingSession(),  # type: ignore[arg-type]
            )


if __name__ == "__main__":
    unittest.main()
