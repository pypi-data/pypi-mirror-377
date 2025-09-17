from rasa.core.policies.enterprise_search_policy import EnterpriseSearchPolicy
from rasa.core.policies.flow_policy import FlowPolicy
from rasa.core.policies.intentless_policy import IntentlessPolicy
from rasa.core.policies.memoization import AugmentedMemoizationPolicy, MemoizationPolicy
from rasa.core.policies.rule_policy import RulePolicy
from rasa.dialogue_understanding.coexistence.intent_based_router import (
    IntentBasedRouter,
)
from rasa.dialogue_understanding.coexistence.llm_based_router import LLMBasedRouter
from rasa.dialogue_understanding.generator import (
    LLMCommandGenerator,
)
from rasa.dialogue_understanding.generator.nlu_command_adapter import NLUCommandAdapter
from rasa.engine.graph import GraphComponent
from rasa.nlu.classifiers.fallback_classifier import FallbackClassifier
from rasa.nlu.classifiers.keyword_intent_classifier import KeywordIntentClassifier
from rasa.nlu.classifiers.logistic_regression_classifier import (
    LogisticRegressionClassifier,
)
from rasa.nlu.classifiers.mitie_intent_classifier import MitieIntentClassifier
from rasa.nlu.classifiers.sklearn_intent_classifier import SklearnIntentClassifier
from rasa.nlu.extractors.crf_entity_extractor import CRFEntityExtractor
from rasa.nlu.extractors.duckling_entity_extractor import DucklingEntityExtractor
from rasa.nlu.extractors.entity_synonyms import EntitySynonymMapper
from rasa.nlu.extractors.mitie_entity_extractor import MitieEntityExtractor
from rasa.nlu.extractors.regex_entity_extractor import RegexEntityExtractor
from rasa.nlu.extractors.spacy_entity_extractor import SpacyEntityExtractor
from rasa.nlu.featurizers.dense_featurizer.mitie_featurizer import MitieFeaturizer
from rasa.nlu.featurizers.dense_featurizer.spacy_featurizer import SpacyFeaturizer
from rasa.nlu.featurizers.sparse_featurizer.count_vectors_featurizer import (
    CountVectorsFeaturizer,
)
from rasa.nlu.featurizers.sparse_featurizer.lexical_syntactic_featurizer import (
    LexicalSyntacticFeaturizer,
)
from rasa.nlu.featurizers.sparse_featurizer.regex_featurizer import RegexFeaturizer
from rasa.nlu.tokenizers.jieba_tokenizer import JiebaTokenizer
from rasa.nlu.tokenizers.mitie_tokenizer import MitieTokenizer
from rasa.nlu.tokenizers.spacy_tokenizer import SpacyTokenizer
from rasa.nlu.tokenizers.whitespace_tokenizer import WhitespaceTokenizer
from rasa.nlu.utils.mitie_utils import MitieNLP
from rasa.nlu.utils.spacy_utils import SpacyNLP
from rasa.shared.utils.common import conditional_import

# Conditional imports for TensorFlow-dependent components
TEDPolicy, TED_POLICY_AVAILABLE = conditional_import(
    "rasa.core.policies.ted_policy", "TEDPolicy"
)
UnexpecTEDIntentPolicy, UNEXPECTED_INTENT_POLICY_AVAILABLE = conditional_import(
    "rasa.core.policies.unexpected_intent_policy", "UnexpecTEDIntentPolicy"
)
DIETClassifier, DIET_CLASSIFIER_AVAILABLE = conditional_import(
    "rasa.nlu.classifiers.diet_classifier", "DIETClassifier"
)
ConveRTFeaturizer, CONVERT_FEATURIZER_AVAILABLE = conditional_import(
    "rasa.nlu.featurizers.dense_featurizer.convert_featurizer", "ConveRTFeaturizer"
)
LanguageModelFeaturizer, LANGUAGE_MODEL_FEATURIZER_AVAILABLE = conditional_import(
    "rasa.nlu.featurizers.dense_featurizer.lm_featurizer", "LanguageModelFeaturizer"
)
ResponseSelector, RESPONSE_SELECTOR_AVAILABLE = conditional_import(
    "rasa.nlu.selectors.response_selector", "ResponseSelector"
)

DEFAULT_COMPONENTS = [
    # Message Classifiers
    FallbackClassifier,
    KeywordIntentClassifier,
    MitieIntentClassifier,
    SklearnIntentClassifier,
    LogisticRegressionClassifier,
    NLUCommandAdapter,
    LLMCommandGenerator,
    LLMBasedRouter,
    IntentBasedRouter,
    # Response Selectors
    # Message Entity Extractors
    CRFEntityExtractor,
    DucklingEntityExtractor,
    EntitySynonymMapper,
    MitieEntityExtractor,
    SpacyEntityExtractor,
    RegexEntityExtractor,
    # Message Feauturizers
    LexicalSyntacticFeaturizer,
    MitieFeaturizer,
    SpacyFeaturizer,
    CountVectorsFeaturizer,
    RegexFeaturizer,
    # Tokenizers
    JiebaTokenizer,
    MitieTokenizer,
    SpacyTokenizer,
    WhitespaceTokenizer,
    # Language Model Providers
    MitieNLP,
    SpacyNLP,
    # Dialogue Management Policies
    RulePolicy,
    MemoizationPolicy,
    AugmentedMemoizationPolicy,
    FlowPolicy,
    EnterpriseSearchPolicy,
    IntentlessPolicy,
]


class ComponentInserter:
    """Manages insertion of components at specific positions with index adjustment."""

    def __init__(self, insertion_points: dict[str, int]):
        self.insertion_points = insertion_points
        self.insertion_counts = {category: 0 for category in insertion_points}

    def insert_if_available(
        self, component: GraphComponent, is_available: bool, category: str
    ) -> None:
        """Insert a component at the appropriate position if available."""
        if is_available and component is not None:
            # Calculate the adjusted index based on insertions in earlier categories
            adjusted_index = self.insertion_points[category]
            for cat, count in self.insertion_counts.items():
                if self.insertion_points[cat] < self.insertion_points[category]:
                    adjusted_index += count

            DEFAULT_COMPONENTS.insert(adjusted_index, component)
            self.insertion_counts[category] += 1


# Define insertion points by component category to preserve order
INSERTION_POINTS = {
    "classifiers": 1,
    "response_selectors": 11,
    "featurizers": 20,
    "policies": 35,
}

# Create inserter instance
inserter = ComponentInserter(INSERTION_POINTS)

# Conditionally add TensorFlow-dependent components
inserter.insert_if_available(DIETClassifier, DIET_CLASSIFIER_AVAILABLE, "classifiers")
inserter.insert_if_available(
    ResponseSelector, RESPONSE_SELECTOR_AVAILABLE, "response_selectors"
)
inserter.insert_if_available(
    ConveRTFeaturizer, CONVERT_FEATURIZER_AVAILABLE, "featurizers"
)
inserter.insert_if_available(
    LanguageModelFeaturizer, LANGUAGE_MODEL_FEATURIZER_AVAILABLE, "featurizers"
)
inserter.insert_if_available(TEDPolicy, TED_POLICY_AVAILABLE, "policies")
inserter.insert_if_available(
    UnexpecTEDIntentPolicy, UNEXPECTED_INTENT_POLICY_AVAILABLE, "policies"
)
