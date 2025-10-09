# Cấu hình CI/CD cho Repository_A

## Vấn đề đã được sửa

Lỗi CI/CD ban đầu:
```
E1009 02:17:13.305642    2078 memcache.go:265] "Unhandled Error" err="couldn't get current server API group list: Get \"http://localhost:8080/api?timeout=32s\": dial tcp [::1]:8080: connect: connection refused"
```

**Nguyên nhân**: Kubectl không thể kết nối đến Kubernetes cluster vì thiếu kubeconfig.

## Giải pháp đã áp dụng

1. **Thêm kubectl setup**: Sử dụng `azure/setup-kubectl@v3` action
2. **Cấu hình kubeconfig**: Đọc từ GitHub secrets
3. **Kiểm tra kết nối**: Verify cluster connection trước khi thực hiện operations
4. **Error handling**: Graceful failure nếu không thể kết nối

## Cấu hình GitHub Secrets

Để CI/CD hoạt động, bạn cần cấu hình các secrets sau trong GitHub repository:

### 1. KUBE_CONFIG_DATA
- **Mô tả**: Kubeconfig file được encode base64
- **Cách tạo**:
  ```bash
  # Lấy kubeconfig từ cluster
  kubectl config view --raw > kubeconfig.yaml
  
  # Encode base64
  cat kubeconfig.yaml | base64 -w 0
  ```
- **Cách thêm vào GitHub**:
  1. Vào repository → Settings → Secrets and variables → Actions
  2. Click "New repository secret"
  3. Name: `KUBE_CONFIG_DATA`
  4. Secret: Paste kết quả base64

### 2. PAT_TOKEN (đã có)
- **Mô tả**: Personal Access Token để push code vào Repository_B
- **Quyền cần thiết**: `repo`, `workflow`

## Cấu trúc workflow đã cập nhật

```yaml
- name: Setup Kubernetes config
  uses: azure/setup-kubectl@v3
  with:
    version: 'latest'
    
- name: Configure kubectl
  run: |
    mkdir -p ~/.kube
    echo "${{ secrets.KUBE_CONFIG_DATA }}" | base64 -d > ~/.kube/config
    kubectl version --client
    kubectl cluster-info || echo "⚠️ Cannot connect to cluster"
    
- name: Force ArgoCD Sync and Delete Old Pods
  run: |
    # Verify connection trước khi thực hiện
    if ! kubectl cluster-info > /dev/null 2>&1; then
      echo "❌ Cannot connect to Kubernetes cluster"
      exit 1
    fi
    # ... rest of the operations
```

## Các bước để test

1. **Cấu hình secrets** theo hướng dẫn trên
2. **Trigger workflow** bằng cách push code hoặc manual trigger
3. **Kiểm tra logs** trong GitHub Actions để đảm bảo:
   - Kubectl được setup thành công
   - Kết nối cluster thành công
   - ArgoCD operations hoạt động

## Troubleshooting

### Lỗi "connection refused"
- Kiểm tra `KUBE_CONFIG_DATA` secret có đúng không
- Verify kubeconfig có thể kết nối đến cluster từ local

### Lỗi "Cannot connect to cluster"
- Kiểm tra cluster endpoint có accessible không
- Verify authentication credentials trong kubeconfig

### Lỗi ArgoCD operations
- Kiểm tra ArgoCD application name và namespace
- Verify permissions để thao tác với ArgoCD resources

## Monitoring

Sau khi fix, bạn có thể monitor:
- GitHub Actions logs
- ArgoCD UI để xem sync status
- Kubernetes pods trong namespace `django-api`

## Lưu ý bảo mật

- Không commit kubeconfig vào code
- Sử dụng GitHub secrets để lưu trữ sensitive data
- Regular rotate PAT_TOKEN và kubeconfig
- Limit permissions của service account trong kubeconfig
