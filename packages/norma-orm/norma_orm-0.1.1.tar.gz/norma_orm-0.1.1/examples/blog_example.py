"""
Norma ORM Blog Example

A comprehensive example showing a blog application with:
- User management
- Post creation and management
- Comments system
- Tag system with many-to-many relationships
- Full CRUD operations
- Relationship loading
"""

import asyncio
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from uuid import uuid4

from norma import BaseModel, Field, NormaClient, OneToMany, ManyToOne, ManyToMany


@dataclass
class User(BaseModel):
    """User model with profile information."""
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: uuid4().hex,
        description="Unique user identifier"
    )
    
    username: str = Field(
        unique=True,
        max_length=50,
        min_length=3,
        index=True,
        description="Unique username"
    )
    
    email: str = Field(
        unique=True,
        max_length=255,
        regex_pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        description="User's email address"
    )
    
    full_name: str = Field(
        max_length=100,
        description="User's full name"
    )
    
    bio: Optional[str] = Field(
        max_length=500,
        default=None,
        description="User biography"
    )
    
    is_active: bool = Field(
        default=True,
        index=True,
        description="Whether the user account is active"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.now,
        index=True,
        description="Account creation timestamp"
    )


@dataclass
class Tag(BaseModel):
    """Tag model for categorizing posts."""
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: uuid4().hex,
        description="Unique tag identifier"
    )
    
    name: str = Field(
        unique=True,
        max_length=50,
        min_length=1,
        index=True,
        description="Tag name"
    )
    
    description: Optional[str] = Field(
        max_length=200,
        default=None,
        description="Tag description"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Tag creation timestamp"
    )


@dataclass
class Post(BaseModel):
    """Blog post model with relationships."""
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: uuid4().hex,
        description="Unique post identifier"
    )
    
    title: str = Field(
        max_length=200,
        min_length=1,
        index=True,
        description="Post title"
    )
    
    slug: str = Field(
        unique=True,
        max_length=200,
        index=True,
        description="URL-friendly post slug"
    )
    
    content: str = Field(
        min_length=1,
        description="Post content in markdown"
    )
    
    excerpt: Optional[str] = Field(
        max_length=300,
        default=None,
        description="Post excerpt for previews"
    )
    
    # Relationship to User
    author_id: str = Field(
        relationship=ManyToOne("User", foreign_key="id"),
        description="ID of the post author"
    )
    
    published: bool = Field(
        default=False,
        index=True,
        description="Whether the post is published"
    )
    
    featured: bool = Field(
        default=False,
        index=True,
        description="Whether the post is featured"
    )
    
    view_count: int = Field(
        default=0,
        description="Number of views"
    )
    
    # Many-to-many relationship with tags
    tag_ids: List[str] = Field(
        relationship=ManyToMany("Tag"),
        default_factory=list,
        description="Associated tag IDs"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.now,
        index=True,
        description="Post creation timestamp"
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="Last update timestamp"
    )
    
    published_at: Optional[datetime] = Field(
        default=None,
        index=True,
        description="Publication timestamp"
    )


@dataclass
class Comment(BaseModel):
    """Comment model for posts."""
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: uuid4().hex,
        description="Unique comment identifier"
    )
    
    content: str = Field(
        min_length=1,
        max_length=1000,
        description="Comment content"
    )
    
    # Relationship to Post
    post_id: str = Field(
        relationship=ManyToOne("Post", foreign_key="id"),
        index=True,
        description="ID of the commented post"
    )
    
    # Relationship to User
    author_id: str = Field(
        relationship=ManyToOne("User", foreign_key="id"),
        description="ID of the comment author"
    )
    
    # Self-referential relationship for replies
    parent_comment_id: Optional[str] = Field(
        relationship=ManyToOne("Comment", foreign_key="id"),
        default=None,
        description="ID of parent comment for replies"
    )
    
    is_approved: bool = Field(
        default=True,
        index=True,
        description="Whether the comment is approved"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.now,
        index=True,
        description="Comment creation timestamp"
    )


class BlogService:
    """Service class for blog operations."""
    
    def __init__(self, client: NormaClient):
        self.client = client
        self.user_client = client.get_model_client(User)
        self.post_client = client.get_model_client(Post)
        self.tag_client = client.get_model_client(Tag)
        self.comment_client = client.get_model_client(Comment)
    
    async def setup_database(self):
        """Create all tables/collections."""
        await self.user_client.create_table()
        await self.tag_client.create_table()
        await self.post_client.create_table()
        await self.comment_client.create_table()
        print("✅ Database tables created")
    
    async def create_sample_data(self):
        """Create sample blog data."""
        
        # Create users
        users_data = [
            {
                "username": "alice",
                "email": "alice@blog.com",
                "full_name": "Alice Johnson",
                "bio": "Tech enthusiast and blogger"
            },
            {
                "username": "bob",
                "email": "bob@blog.com", 
                "full_name": "Bob Smith",
                "bio": "Software developer and writer"
            }
        ]
        
        created_users = []
        for user_data in users_data:
            user = User(**user_data)
            created_user = await self.user_client.insert(user)
            created_users.append(created_user)
            print(f"✅ Created user: {created_user.username}")
        
        # Create tags
        tags_data = [
            {"name": "python", "description": "Python programming language"},
            {"name": "web-development", "description": "Web development topics"},
            {"name": "tutorial", "description": "Tutorial content"},
            {"name": "orm", "description": "Object-Relational Mapping"}
        ]
        
        created_tags = []
        for tag_data in tags_data:
            tag = Tag(**tag_data)
            created_tag = await self.tag_client.insert(tag)
            created_tags.append(created_tag)
            print(f"✅ Created tag: {created_tag.name}")
        
        # Create posts
        posts_data = [
            {
                "title": "Getting Started with Norma ORM",
                "slug": "getting-started-with-norma-orm",
                "content": "# Getting Started with Norma ORM\n\nNorma is a modern Python ORM...",
                "excerpt": "Learn how to get started with Norma ORM",
                "author_id": created_users[0].id,
                "published": True,
                "published_at": datetime.now(),
                "tag_ids": [created_tags[0].id, created_tags[3].id]
            },
            {
                "title": "Advanced Query Patterns",
                "slug": "advanced-query-patterns",
                "content": "# Advanced Query Patterns\n\nThis post covers advanced querying...",
                "excerpt": "Advanced querying techniques with Norma",
                "author_id": created_users[1].id,
                "published": True,
                "published_at": datetime.now(),
                "tag_ids": [created_tags[0].id, created_tags[2].id]
            },
            {
                "title": "Building Web APIs with Norma",
                "slug": "building-web-apis-with-norma",
                "content": "# Building Web APIs\n\nLearn how to build APIs...",
                "excerpt": "Building modern web APIs",
                "author_id": created_users[0].id,
                "published": False,
                "tag_ids": [created_tags[1].id, created_tags[2].id]
            }
        ]
        
        created_posts = []
        for post_data in posts_data:
            post = Post(**post_data)
            created_post = await self.post_client.insert(post)
            created_posts.append(created_post)
            print(f"✅ Created post: {created_post.title}")
        
        # Create comments
        comments_data = [
            {
                "content": "Great introduction to Norma ORM! Very helpful.",
                "post_id": created_posts[0].id,
                "author_id": created_users[1].id
            },
            {
                "content": "Thanks for the detailed explanation.",
                "post_id": created_posts[0].id,
                "author_id": created_users[0].id
            },
            {
                "content": "Looking forward to more advanced topics!",
                "post_id": created_posts[1].id,
                "author_id": created_users[0].id
            }
        ]
        
        created_comments = []
        for comment_data in comments_data:
            comment = Comment(**comment_data)
            created_comment = await self.comment_client.insert(comment)
            created_comments.append(created_comment)
            print(f"✅ Created comment on post: {created_comment.post_id[:8]}...")
        
        return {
            'users': created_users,
            'tags': created_tags,
            'posts': created_posts,
            'comments': created_comments
        }
    
    async def demonstrate_queries(self):
        """Demonstrate various query patterns."""
        
        print("\n🔍 Query Demonstrations")
        print("=" * 30)
        
        # Find all published posts
        published_posts = await self.post_client.find_many({"published": True})
        print(f"📄 Found {len(published_posts)} published posts")
        
        # Find posts by specific author
        users = await self.user_client.find_many({"username": "alice"})
        if users:
            alice = users[0]
            alice_posts = await self.post_client.find_many({"author_id": alice.id})
            print(f"✍️  Alice has written {len(alice_posts)} posts")
        
        # Find posts with specific tags
        python_tag = await self.tag_client.find_many({"name": "python"})
        if python_tag:
            python_posts = await self.post_client.find_many({
                "tag_ids": {"$in": [python_tag[0].id]}
            })
            print(f"🐍 Found {len(python_posts)} Python-related posts")
        
        # Complex query: published posts sorted by date
        recent_posts = await self.post_client.find_many(
            filters={"published": True},
            order_by=["-published_at"],
            limit=5
        )
        print(f"📅 {len(recent_posts)} most recent published posts")
        
        # Find comments for a specific post
        if published_posts:
            post_comments = await self.comment_client.find_many({
                "post_id": published_posts[0].id
            })
            print(f"💬 Found {len(post_comments)} comments on '{published_posts[0].title}'")
        
        # Count queries
        total_users = await self.user_client.count()
        total_posts = await self.post_client.count()
        published_count = await self.post_client.count({"published": True})
        
        print(f"\n📊 Statistics:")
        print(f"   Users: {total_users}")
        print(f"   Total posts: {total_posts}")
        print(f"   Published posts: {published_count}")
    
    async def demonstrate_updates(self):
        """Demonstrate update operations."""
        
        print("\n📝 Update Demonstrations")
        print("=" * 30)
        
        # Find a draft post and publish it
        draft_posts = await self.post_client.find_many({"published": False})
        if draft_posts:
            draft = draft_posts[0]
            draft.published = True
            draft.published_at = datetime.now()
            draft.updated_at = datetime.now()
            
            updated_post = await self.post_client.update(draft)
            print(f"📢 Published post: {updated_post.title}")
        
        # Update user profile
        users = await self.user_client.find_many({"username": "bob"})
        if users:
            bob = users[0]
            bob.bio = "Updated bio: Senior software developer and technical writer"
            updated_user = await self.user_client.update(bob)
            print(f"👤 Updated user profile: {updated_user.username}")
        
        # Increment view count for a post
        if draft_posts:
            post = draft_posts[0]
            post.view_count += 1
            await self.post_client.update(post)
            print(f"👁️  Incremented view count for: {post.title}")
    
    async def demonstrate_advanced_features(self):
        """Demonstrate advanced ORM features."""
        
        print("\n🚀 Advanced Features")
        print("=" * 30)
        
        # Batch operations
        posts = await self.post_client.find_many(limit=2)
        for post in posts:
            post.view_count += 5
        
        print(f"📈 Updated view counts for {len(posts)} posts")
        
        # Complex filters
        popular_posts = await self.post_client.find_many({
            "published": True,
            "view_count": {"$gte": 0}
        })
        print(f"🔥 Found {len(popular_posts)} posts with views")
        
        # Search functionality (simplified)
        search_results = await self.post_client.find_many({
            "title": {"$regex": "Norma"}  # This would be adapter-specific
        })
        print(f"🔍 Search found {len(search_results)} posts mentioning 'Norma'")


async def main():
    """Main blog example function."""
    
    print("📝 Norma ORM Blog Example")
    print("=" * 50)
    
    # Initialize client (using SQLite for demo)
    client = NormaClient(
        adapter_type="sql",
        database_url="sqlite:///./blog_example.db",
        echo=False  # Set to True to see SQL queries
    )
    
    async with client:
        # Initialize blog service
        blog_service = BlogService(client)
        
        # Setup database
        await blog_service.setup_database()
        
        # Create sample data
        print("\n📊 Creating Sample Data")
        print("=" * 30)
        sample_data = await blog_service.create_sample_data()
        
        # Demonstrate queries
        await blog_service.demonstrate_queries()
        
        # Demonstrate updates
        await blog_service.demonstrate_updates()
        
        # Demonstrate advanced features
        await blog_service.demonstrate_advanced_features()
        
        print("\n🎉 Blog example completed!")
        print("\nThe blog database has been created with:")
        print(f"  - {len(sample_data['users'])} users")
        print(f"  - {len(sample_data['tags'])} tags") 
        print(f"  - {len(sample_data['posts'])} posts")
        print(f"  - {len(sample_data['comments'])} comments")
        print("\nYou can examine the SQLite database file: blog_example.db")


if __name__ == "__main__":
    asyncio.run(main())
