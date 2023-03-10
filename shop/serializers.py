

from rest_framework import serializers

from shop.models import ImagesProduct, Product
# from shop.services import representation


class ImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagesProduct
        fields = ('image',)


class ProductListSerializer(serializers.ModelSerializer):
    detail = serializers.HyperlinkedIdentityField(view_name='detail_product', lookup_field='slug', read_only=True)
    images = serializers.SerializerMethodField()
    category = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Product
        fields = ('detail', 'brand', 'name',
                  'price', 'discount', 'new_price',
                  'in_stock', 'quantity', 'category', 'images',
                  )

    def to_representation(self, obj):
        rep = super().to_representation(obj)
        if obj.new_price is None:
            rep.pop('new_price')
            rep.pop('discount')
        else:
            rep['old_price'] = rep['price']
            rep.pop('price')
        return rep


    def get_images(self, obj):
        request = self.context.get('request')
        images = obj.images.all().first().image
        return request.build_absolute_uri(images.url)


class ProductDetailSerializer(serializers.ModelSerializer):
    images = ImagesSerializer(many=True, read_only=True)
    category = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Product
        fields = '__all__'

    def to_representation(self, obj):
        rep = super().to_representation(obj)
        if obj.new_price is None:
            rep.pop('new_price')
            rep.pop('discount')
        else:
            rep['old_price'] = rep['price']
            rep.pop('price')
        return rep
