from haystack import fields
from haystack.indexes import SearchIndex


class EvaluatedItemIndex(SearchIndex):

    evaluated_rubrics = fields.MultiValueField(model_attr="evaluated_rubrics", null=True)

    evaluation_score_rubric_0 = fields.FloatField(model_attr="evaluation_score_rubric_0", null=True)
    evaluation_score_rubric_1 = fields.FloatField(model_attr="evaluation_score_rubric_1", null=True)
    evaluation_score_rubric_2 = fields.FloatField(model_attr="evaluation_score_rubric_2", null=True)
    evaluation_score_rubric_3 = fields.FloatField(model_attr="evaluation_score_rubric_3", null=True)
    evaluation_score_rubric_4 = fields.FloatField(model_attr="evaluation_score_rubric_4", null=True)
    evaluation_score_rubric_5 = fields.FloatField(model_attr="evaluation_score_rubric_5", null=True)
    evaluation_score_rubric_6 = fields.FloatField(model_attr="evaluation_score_rubric_6", null=True)
