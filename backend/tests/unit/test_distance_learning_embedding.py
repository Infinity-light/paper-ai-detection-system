"""
单元测试：Distance Learning Detector - Embedding 功能
测试 SiliconFlow Embedding API 集成
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from app.core.distance_learning import DistanceLearningDetector, EmbeddingAPIError


@pytest.fixture
def mock_detector():
    """创建带 mock 环境变量的检测器"""
    with patch.dict('os.environ', {
        'DEEPSEEK_API_KEY': 'test-deepseek-key',
        'SILICONFLOW_API_KEY': 'test-siliconflow-key'
    }):
        detector = DistanceLearningDetector()
        return detector


class TestCosineSimilarity:
    """测试余弦相似度计算"""

    def test_identical_vectors(self, mock_detector):
        """测试相同向量的相似度应该为1"""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [1.0, 2.0, 3.0]
        similarity = mock_detector._cosine_similarity(vec1, vec2)
        assert abs(similarity - 1.0) < 1e-6

    def test_orthogonal_vectors(self, mock_detector):
        """测试正交向量的相似度应该为0"""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 1.0, 0.0]
        similarity = mock_detector._cosine_similarity(vec1, vec2)
        assert abs(similarity - 0.0) < 1e-6

    def test_opposite_vectors(self, mock_detector):
        """测试相反向量的相似度应该为-1"""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [-1.0, -2.0, -3.0]
        similarity = mock_detector._cosine_similarity(vec1, vec2)
        assert abs(similarity - (-1.0)) < 1e-6

    def test_normalized_vectors(self, mock_detector):
        """测试归一化向量"""
        vec1 = [3.0, 4.0]  # length = 5
        vec2 = [4.0, 3.0]  # length = 5
        similarity = mock_detector._cosine_similarity(vec1, vec2)
        # cos(θ) = (3*4 + 4*3) / (5*5) = 24/25 = 0.96
        assert abs(similarity - 0.96) < 1e-6

    def test_zero_vector_handling(self, mock_detector):
        """测试零向量处理"""
        vec1 = [0.0, 0.0, 0.0]
        vec2 = [1.0, 2.0, 3.0]
        similarity = mock_detector._cosine_similarity(vec1, vec2)
        assert similarity == 0.0


class TestGetEmbedding:
    """测试 Embedding API 调用"""

    @patch('app.core.distance_learning.requests.post')
    def test_successful_api_call(self, mock_post, mock_detector):
        """测试成功的API调用"""
        # Mock 响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "embedding": [0.1, 0.2, 0.3, 0.4, 0.5]
                }
            ]
        }
        mock_post.return_value = mock_response

        embedding = mock_detector._get_embedding("测试文本")

        assert embedding == [0.1, 0.2, 0.3, 0.4, 0.5]
        mock_post.assert_called_once()

    @patch('app.core.distance_learning.requests.post')
    def test_api_error_handling(self, mock_post, mock_detector):
        """测试API错误处理"""
        # Mock 失败响应
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response

        with pytest.raises(EmbeddingAPIError) as exc_info:
            mock_detector._get_embedding("测试文本")

        assert exc_info.value.status_code == 401
        assert "Unauthorized" in exc_info.value.response_text

    @patch('app.core.distance_learning.requests.post')
    def test_network_timeout(self, mock_post, mock_detector):
        """测试网络超时"""
        mock_post.side_effect = Exception("Connection timeout")

        with pytest.raises(EmbeddingAPIError) as exc_info:
            mock_detector._get_embedding("测试文本")

        assert "Connection timeout" in str(exc_info.value)

    @patch('app.core.distance_learning.requests.post')
    def test_invalid_response_format(self, mock_post, mock_detector):
        """测试无效的响应格式"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": []  # 空数据
        }
        mock_post.return_value = mock_response

        with pytest.raises(EmbeddingAPIError):
            mock_detector._get_embedding("测试文本")


class TestCalculateSemanticDistance:
    """测试语义距离计算"""

    @patch.object(DistanceLearningDetector, '_get_embedding')
    def test_identical_texts(self, mock_get_embedding, mock_detector):
        """测试相同文本的距离应该接近0"""
        # Mock 返回相同的 embedding
        mock_get_embedding.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]

        distance = mock_detector._calculate_semantic_distance("文本A", "文本A")

        # 相同文本，相似度=1，距离=0
        assert abs(distance - 0.0) < 1e-6

    @patch.object(DistanceLearningDetector, '_get_embedding')
    def test_different_texts(self, mock_get_embedding, mock_detector):
        """测试不同文本的距离"""
        # Mock 返回不同的 embedding
        def side_effect(text):
            if "文本A" in text:
                return [1.0, 0.0, 0.0]
            else:
                return [0.0, 1.0, 0.0]

        mock_get_embedding.side_effect = side_effect

        distance = mock_detector._calculate_semantic_distance("文本A", "文本B")

        # 正交向量，相似度=0，距离=1
        assert abs(distance - 1.0) < 1e-6

    @patch.object(DistanceLearningDetector, '_get_embedding')
    def test_similar_texts(self, mock_get_embedding, mock_detector):
        """测试相似文本的距离"""
        # Mock 返回相似的 embedding
        def side_effect(text):
            if "文本A" in text:
                return [1.0, 0.1, 0.0]
            else:
                return [0.9, 0.2, 0.0]

        mock_get_embedding.side_effect = side_effect

        distance = mock_detector._calculate_semantic_distance("文本A", "文本B")

        # 相似向量，距离应该较小
        assert 0.0 < distance < 0.5


class TestDetectorInitialization:
    """测试检测器初始化"""

    def test_missing_deepseek_api_key(self):
        """测试缺少 Deepseek API Key"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="需要提供DEEPSEEK_API_KEY"):
                DistanceLearningDetector()

    def test_missing_siliconflow_api_key(self):
        """测试缺少 SiliconFlow API Key"""
        with patch.dict('os.environ', {'DEEPSEEK_API_KEY': 'test-key'}):
            with patch('app.core.distance_learning.get_settings') as mock_settings:
                mock_settings.return_value.siliconflow_api_key = None

                with pytest.raises(ValueError, match="需要在配置中提供 siliconflow_api_key"):
                    DistanceLearningDetector()

    def test_successful_initialization(self):
        """测试成功初始化"""
        with patch.dict('os.environ', {'DEEPSEEK_API_KEY': 'test-key'}):
            with patch('app.core.distance_learning.get_settings') as mock_settings:
                mock_settings.return_value.siliconflow_api_key = 'sf-test-key'
                mock_settings.return_value.siliconflow_api_base = 'https://api.siliconflow.cn/v1'
                mock_settings.return_value.siliconflow_model = 'BAAI/bge-large-zh-v1.5'

                detector = DistanceLearningDetector()

                assert detector.api_key == 'test-key'
                assert detector.siliconflow_api_key == 'sf-test-key'
                assert detector.siliconflow_model == 'BAAI/bge-large-zh-v1.5'


class TestEdgeCases:
    """测试边界情况"""

    def test_empty_text(self, mock_detector):
        """测试空文本"""
        result = mock_detector.detect("")

        assert result['ai_probability'] == 0
        assert result['distance'] == 0
        assert result['confidence'] == 'low'
        assert 'error' in result

    def test_short_text(self, mock_detector):
        """测试过短文本"""
        result = mock_detector.detect("短文本")

        assert result['ai_probability'] == 0
        assert result['confidence'] == 'low'
        assert 'error' in result

    @patch.object(DistanceLearningDetector, '_rewrite_text')
    @patch.object(DistanceLearningDetector, '_calculate_semantic_distance')
    def test_valid_text_processing(self, mock_distance, mock_rewrite, mock_detector):
        """测试有效文本处理流程"""
        mock_rewrite.return_value = "改写后的文本"
        mock_distance.return_value = 0.15  # AI文本的典型距离

        result = mock_detector.detect("这是一段足够长的测试文本，用于验证检测功能是否正常工作。")

        assert 'ai_probability' in result
        assert 'distance' in result
        assert 'confidence' in result
        assert result['ai_probability'] > 0
