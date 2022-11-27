from rest_framework import serializers

from .models import BookModel, BookLibraryModel, LibraryModel


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookModel
        fields = "__all__"


class BookLibrarySerializer(serializers.ModelSerializer):
    book_uid = serializers.UUIDField(source="book_id.book_uid")
    name = serializers.CharField(source="book_id.name", max_length=255)
    author = serializers.CharField(source="book_id.author", max_length=255)
    genre = serializers.CharField(source="book_id.genre", max_length=255)
    condition = serializers.CharField(source="book_id.condition", max_length=20)

    class Meta:
        model = BookLibraryModel
        depth = 1
        fields = (
            "id", "available_count", "book_uid", "name",
            "author", "genre", "condition",
        )


class BookUUIDLibraryUUIDSerializer(serializers.ModelSerializer):
    book_uid = serializers.UUIDField(source="book_id.book_uid", read_only=True)
    name = serializers.CharField(source="book_id.name", max_length=255, read_only=True)
    author = serializers.CharField(source="book_id.author", max_length=255, read_only=True)
    genre = serializers.CharField(source="book_id.genre", max_length=255, read_only=True)
    condition = serializers.CharField(source="book_id.condition", max_length=20, read_only=True)

    class Meta:
        model = BookLibraryModel
        fields = (
            "id", "available_count", "book_uid", "name",
            "author", "genre", "condition",
        )


class LibrarySerializer(serializers.ModelSerializer):
    books = BookSerializer(many=True)

    class Meta:
        model = LibraryModel
        fields = "__all__"


class LibraryWithoutBooksSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryModel
        exclude = ("books",)
