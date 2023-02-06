from django.test import TestCase
import datetime
from django.utils import timezone
from django.urls import reverse

from .models import Question
# Create your tests here.

class QuestionModelTests(TestCase):

  def test_was_published_recently_with_future_question(self):
    """
      was_published_recently()はpubdateが現在時刻より未来に設定された
      場合はFalseを返さないといけない。
    """
    time = timezone.now() + datetime.timedelta(days=30)
    future_question = Question(pub_date=time)
    # ここで返却値がFalse出ない場合はテストに通らない事を設定している。
    self.assertIs(future_question.was_published_recently(), False)

  # 新しくテストを追加していく。
  def test_was_published_recently_with_old_question(self):
    """
      was_published_recently()はpub_dateが1日より過去の場合
      Falseを返す
    """
    # 現在時刻より一日1秒前の質問のインスタンスを作成する。
    time = timezone.now() - datetime.timedelta(days=1, seconds=1)
    old_question = Question(pub_date=time)
    # 返り値がFalseならテストに通る。
    self.assertIs(old_question.was_published_recently(), False)

  def test_was_published_recently_with_recent_question(self):
    """
      was_published_recently()はpub_dateが1日以内ならTrueを返す
    """
    # 一日以内の質問インスタンスを作成する。
    time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
    recent_question = Question(pub_date=time)
    self.assertIs(recent_question.was_published_recently(), True)

def create_question(question_text, days):
    """
        引数から質問を作成する。過去に投稿された質問を作りたいなら-1~nの値を第二引数に取る、
        まだ公開されてない質問を作成したいなら+1~nの値を第二引数に取る。
        現在から10日後の投稿日の質問を作成したいなら
        例： create_question('今日は何食べる?' , 10)

    　　　　15日前の質問を作成したいなら
            create_question('今日は何食べる?' , -15)
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QestionIndexViewTests(TestCase):
  def test_no_question(self):
    """
      質問がデータベースにない際に適切なメッセージを
      表示出来てるか確認する。
    """
    response = self.client.get(reverse('polls:index'))
    # テスト合格条件
    # ステータスコードが200である事
    self.assertEqual(response.status_code, 200)
    # コンテンツに No polls are availableが含まれる事
    self.assertContains(response, "No polls are available.")
    # データベースが空である事
    self.assertQuerysetEqual(response.context['latest_question_list'], [])

  def test_past_question(self):
    """
      過去の投稿日の質問一覧が表示されるか確認する。
    """
    # 投稿日が30日前の質問を作成する。ダミーデータなので実際のデータベースにデータ作成されることはない。
    # そしてメソッドが終了すればダミーデータは破棄される。
    # なので新しくテストする際は質問は空の状態から始まる。
    question = create_question(question_text="過去の質問", days=-30)
    response = self.client.get(reverse('polls:index'))
    # テスト合格条件
    # 先ほど作成した質問が表示されているか表示する。
    self.assertQuerysetEqual(response.context['latest_quesiton_list'], [question],)

  def test_future_question(self):
    """
      投稿日が未来の質問が表示されていないか確認する。
    """
    create_question(question_text="未来の質問", days=30)
    response = self.client.get(reverse('polls:index'))
    # テスト合格条件
    # コンテンツに No polls are awailableが含まれる事
    self.assertContains(response, "No polls are available.")
    # 最新の質問5件が質問が空な事
    self.assertQuerysetEqual(response.context['latest_question_list'], [])

  def test_future_question_and_past_question(self):
    """
      過去・未来の質問の両方ある時に過去の質問だけ表示される。
    """
    # 片方だけ変数に入れるのはテストの合格条件を判別する際に過去質問が表示されているのを確認するため
    question = create_question(question_text="Past question.", days=-30)
    create_question(question_text="Future question.", days=30)
    response = self.client.get(reverse('polls:index'))
    self.assertQuerysetEqual(
      response.context['latest_question_list'],
      [question],
     )

    def test_two_past_questions(self):
      """
        過去の質問2つが表示されているか確認する。
      """
      question1 = create_question(question_text="Past question 1.", days=-30)
      question2 = create_question(question_text="Past question 2.", days=-5)
      response = self.client.get(reverse('polls:index'))
      self.assertQuerysetEqual(
        response.context['latest_question_list'],
        [question2, question1],
      )